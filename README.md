# DRIC
Drone Remote Inspector and Controller

## Requirements
Python 2

## Easy installation
Download the last release from https://github.com/Arth-ur/DRIC/releases.

Unzip the downloaded archive. 

Then, in the terminal:
```
pip install -r requirements.txt
```

## Installation from source
Requirements: node.js with npm. 

Clone the repository. 

Then, in the terminal:

```
pip install -r requirements.txt
cd dricgcss_index
npm install
npm run build
```

## Usage
```
python main.py
```
Connect to the application on `localhost:8000`. 

The backend server is started on `localhost:9555`.

## Front-end development server
Requires node.js and npm.
```
cd dricgcss_index
npm run dev
```
Connect to the application on `localhost:8080`.
