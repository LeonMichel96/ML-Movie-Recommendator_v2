import streamlit as st


st.set_page_config(page_title='Movie Recommendator', page_icon=':movie_camera:', layout='wide')

pages = {'General ✅':[st.Page('pages/1_🚀_Intro.py', default=True)],
         'Data Science 🔮':[st.Page('pages/2_📹_Recommendator.py'),st.Page('pages/3_🤖_Text_to_SQL.py')]}

pg = st.navigation(pages)
pg.run()
