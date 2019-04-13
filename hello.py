# import the nessecary pieces from Flask
from flask import Flask,render_template, request,jsonify,Response
from flask import Markup
import pandas as pd
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


#Create the app object that will route our calls
app = Flask(__name__)
# Add a single endpoint that we can use for testing

@app.route('/', methods = ['GET'])
def home():
    return render_template('maindashboard.html')
#When run from command line, start the server

@app.route('/dashboard')
def my_dashboard():
    return render_template('dashboard.html')

@app.route('/product')
def my_product():
    return render_template('display_product.html')

@app.route('/product', methods=['POST'])
def my_product_post():
	global productname
	productname = request.form['product']
	return productname


@app.route('/form')
def my_form():
    return render_template('form.html')

@app.route('/form', methods=['POST'])
def my_form_post():
	global processed_text,processed_text1
	text = request.form['text']
	processed_text = text
	text1 = request.form['text1']
	processed_text1 = text1
	return shop_basket()

@app.route('/form')

def shop_basket():
	def data_load():
		global df
		print("file loading.........................")
		print(processed_text)
		df = pd.read_excel('OnlineRetail1.xlsx')
		print("file loaded")

	def data_preparation():
	    
	    df['Description'] = df['Description'].str.strip()
	    df.dropna(axis = 0, subset=['InvoiceNo'], inplace = True)
	    df['InvoiceNo'] = df['InvoiceNo'].astype('str')
	    df = df[~df['InvoiceNo'].str.contains('C')] 
	    df = df[~df['Country'].str.contains('United Kingdom')] 
	    df = df[~df['Description'].str.contains('Manual')]
	    df = df[~df['Description'].str.contains('POSTAGE')] 
	    df = df[~df['Description'].str.startswith('?')]
	    
	def country_quantity():
	    global df1_quantity
	    df1_quantity = df.groupby('Country').count().reset_index().sort_values('InvoiceNo', ascending = False).head()
	    return df1_quantity
	    
	def country_price():
	    global df1_price
	    df1_price = df.groupby('Country').sum().reset_index().sort_values('UnitPrice', ascending = False).head()
	    return df1_price

	def top_bought_product(country):
	    germany = df[df['Country']==country]
	    group_germany = germany.groupby(["Description","StockCode"]).sum().reset_index().sort_values('UnitPrice', ascending = False)
	    return group_germany.head(7)

	def sum_to_boolean(x):
	    if x<=0:
	        return 0
	    else:
	        return 1

	def shopping_basket(country):
		print('inside function')
		print(country)
		data_load()
		Basket_France = (df[df['Country']==country]
	              .groupby(['InvoiceNo', 'Description'])['Quantity']
	              .sum().unstack().reset_index().fillna(0)
	              .set_index('InvoiceNo'))
		Basket_Final_France = Basket_France.applymap(sum_to_boolean)
		# Basket_Final_France.drop('POSTAGE', inplace=True, axis=1)
		Frequent_itemsets_France = apriori(Basket_Final_France, min_support = 0.05, use_colnames = True)
		Asso_Rules_France = association_rules(Frequent_itemsets_France, metric = "lift", min_threshold = 1)
		Asso_Rules_France[ (Asso_Rules_France['lift'] >= 4) & (Asso_Rules_France['confidence'] >= 0.5) ]
		a=Asso_Rules_France.sort_values('lift',ascending = False)

		str1 = a.head(7)
		str1['antecedents'] = str1['antecedents'].map(lambda x: ", ".join(x))
		str1['consequents'] = str1['consequents'].map(lambda x: ", ".join(x))
		asd = str1[['antecedents','consequents']]
		# str1['antecendents']=str1['antecedents'].astype('str')
		# str1['antecendents'] = str1['antecendents'].map(lambda x: ", ".join(x)				
		# str1['consequents'] = str1['consequents'].map(lambda x: ", ".join(x)
		pd.set_option('display.max_colwidth', -1)
		value = Markup(asd.to_html(index  = False))	

		return value

	def displayproduct():
		if processed_text != "":
			if processed_text1 != "":
				print("case1")
				return render_template('form.html',abc1 = processed_text1, abc = processed_text, myvar = shopping_basket(processed_text),myvar1 = shopping_basket(processed_text1))
			print("Case2")
			return render_template('form.html',abc1="",myvar1="",abc = processed_text, myvar = shopping_basket(processed_text))
			
		elif processed_text1 != "":
			print("case3")
			return render_template('form.html',abc="", myvar="", abc1 = processed_text1, myvar1 = shopping_basket(processed_text1))
		# return 'hello'
	print("country is")
	print(processed_text)
	shop = displayproduct()
	return shop




if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)

