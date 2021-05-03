![example workflow](https://github.com/prosoffice/wallet-p/actions/workflows/.github/workflows/app.yml/badge.svg)

## WALLET-P API

Wallet-p is a custom wallet system, a REST-based programming interface built with Python, using Flask, a light/micro framework. The API is designed to allow seamless e-commerce transactions across multiple currencies.

API DOCS - https://prosperdev.medium.com/api-documentation-wallet-p-8562830f7a13

HOSTED APPLICATION LINK - https://wallet-p.herokuapp.com/



##### TECHNOLOGIES

- REST - API
- FLASK - Python micro Web framework
- POSTGRESQL - Database
- HEROKU - Hosting service
- Github Actions - Continuous integration (CI)


ADMIN LOGIN CREDENTIALS
`
{
  "email": "admin@gmail.com",
  "password": "testpass"
}
`
#### GETTING STARTED LOCALLY (UBUNTU/MAC OS)

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
  
## IMPORTANT NOTE
Please edit the config file as well as the test file. Hardcode your custom database uri in the relevant variables. I know it's bad design and that will be fixed upon next release. Thanks :) 

Also 'Getting started locally' instructions for **Windows OS** will be release in due course. 
