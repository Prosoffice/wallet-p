

![example workflow](https://github.com/prosoffice/wallet_p/actions/workflows/.github/workflows/app.yml/badge.svg)


# WALLET-P API

Wallet-p is a custom wallet system, a REST-based programming interface built with Python, using Flask, a light Python framework. The API is designed to allow seamless e-commerce transactions across multiple currencies.

**API DOCS** - https://prosperdev.medium.com/api-documentation-wallet-p-8562830f7a13

**HOSTED APPLICATION LINK** - https://wallet-p.herokuapp.com/

### TECHNOLOGIES

This REST-based programming interface is built with Flask, a light/micro framework writted in Python.


**ADMIN LOGIN CREDENTIALS**
`
{
  "email": "admin@gmail.com",
  "password": "testpass"
}
`
#### GETTING STARTED LOCALLY

1. Clone this repo: 
  
  `git clone https://github.com/Prosoffice/wallet-p.git`

2. Change to the repo directory: 
  
  `cd wallet-p`

3. Setup a virtual environment: 
  
  `python3 -m venv env`  & `source env/bin/activate`
  
4. Install dependencies with pip3

  `pip3 install -r requirements.txt`
  
5. Run application
  
  `flask run`

