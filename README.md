# PDS
# 🚀 Streamlit Cloud Deployment Guide for Oxfordshire Data Explorer

## ✅ What you need

* GitHub Account (free)
* Streamlit Account (sign in with GitHub)
* The following project files:

  * `streamlit_app.py`
  * `oxfordshire_data_fixed.db`
  * `CouncilTaxData.xml`
  * `requirements.txt` (optional but recommended)

## 📦 Step 1: Prepare your project folder

Create a folder on your computer and place these files inside:

```
/streamlit_app.py
/oxfordshire_data_fixed.db
/CouncilTaxData.xml
/requirements.txt (optional)
```

If you don't have `requirements.txt`, create one with the following content:

```
pandas
streamlit
matplotlib
```

This helps Streamlit Cloud automatically install the required Python packages.

## 📤 Step 2: Upload to GitHub

1. Login to [https://github.com](https://github.com)
2. Create a new repository → name it something like `oxfordshire-data-explorer`
3. Upload all the files into the repository. Make sure they are in the root folder (not inside subfolders).

Structure should look like:

```
streamlit_app.py
oxfordshire_data_fixed.db
CouncilTaxData.xml
requirements.txt
```

## ☁️ Step 3: Deploy on Streamlit Cloud

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click **New App** in the Streamlit Cloud dashboard
4. Select your GitHub repository
5. Choose the branch (usually `main`)
6. Select `streamlit_app.py` as the main app file
7. Click **Deploy**

✅ Your app will start deploying. After a minute or so, you will get a public URL like:

```
https://yourusername-yourreponame.streamlit.app
```

You can now share this link with anyone (including your coursework submission) and they can interact with your app live in the browser.

## 📌 Notes

* Every time you update your GitHub repository, the Streamlit app will auto-update.
* If you encounter errors, check the logs → usually missing libraries which can be fixed by updating `requirements.txt`.
* Streamlit Community Cloud is free and perfect for coursework or demos.

## 🎉 Done!

You now have a professional, live, and interactive data science web app deployed.

---

End of Deployment Guide
