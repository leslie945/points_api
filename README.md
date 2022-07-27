# About
## Language & Libraries
* Python3 - v3.9.13
* Pip - v22.2
* Installed via Pip
    * FastAPI  - v0.79.0
    * Pydantic - v1.9.1
    * Requests - v2.28.1
    * uvicorn[standard] - v0.18.2

## How to Run
1. Install Python3
2. Use pip to install libraries listed in via pip section above
3. Add Python bin to $PATH, example below

   `PATH = <path_to_python>/bin:PATH`
4. Run app using the command below:

   `$ uvicorn main:app --reload`

5. It is suggested to use swagger for testing, Swagger available at: http://localhost:8000/docs
6. Tests can be run from main folder using following command:

   `$ python -m unittest ./tests/test_main.py
