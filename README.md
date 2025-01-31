# BAWAG_challange

Streamlit application to analyze online retail stores data
It shows:

- Data preview
- Total views & purchases of different categories by site

You can filter by site or choose various categories (multiple selection available)

---

To run the application locally, you'll need:

1. pandas
2. plotly express
3. streamlit

You can run this code to install them all: `pip install pandas plotly-express streamlit`

Then run `streamlit run main.py` to open the app in the browser.

Or you can use docker container:

- `docker build -t my-streamlit-app .`
- `docker run -p 8501:8501 my-streamlit-app`
