import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import os

# 경고 메시지 숨기기
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="수퍼마켓 EDA", 
    page_icon=":bar_chart:",
    layout="wide"
    )

# 제목
st.title(" :bar_chart: 미국 수퍼마켓 데이터 EDA") 
st.caption("[출처(https://www.youtube.com/watch?app=desktop&v=7yAw1nPareM)](https://www.youtube.com/watch?app=desktop&v=7yAw1nPareM)")

# 파일 업로더 설정
file = st.file_uploader(
    ":file_folder: 파일을 업로드 해주세요.",
    type=(["csv","txt","xlsx","xls"])
    )

# 파일이 업로드 되었을 때 처리
if file is not None:
    # 파일명 저장 및 결과 출력
    filepath = os.path.join("./data", file.name)
    st.write(f'{file.name} 파일이 업로드 되었습니다.')
    # 파일 저장
    with open(filepath, "wb") as f:
        f.write(file.getbuffer())
    st.success(f'{file.name} 파일이 data 폴더에 저장되었습니다.')
    # 데이터프레임으로 변환
    df = pd.read_csv(filepath)
else:
    # 저장된 데이터 불러오기
    df = pd.read_csv("./data/Superstore.csv")

# 화면을 2개의 컬럼으로 나누기
col1, col2 = st.columns((2))

# Order Date를 날짜형으로 변환
df["Order Date"] = pd.to_datetime(df["Order Date"])

# 시작일과 종료일 설정
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

# 시작일과 종료일을 선택
with col1:
    date1 = pd.to_datetime(st.date_input("시작일", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("종료일", endDate))

# 날짜에 따라 데이터프레임 필터링
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# 사이드바 설정
st.sidebar.header("데이터 필터: ")

# 지역 선택 다중선택 사이드바
region = st.sidebar.multiselect("지역 선택(복수 가능)", df["Region"].unique())

if not region:
    df_region = df.copy()
else:
    df_region = df[df["Region"].isin(region)]

# 주 선택 다중선택 사이드바
state = st.sidebar.multiselect("주 선택(복수 가능)", df_region["State"].unique())

if not state:
    df_state = df_region.copy()
else:
    df_state = df_region[df_region["State"].isin(state)]

# 도시 선택 다중선택 사이드바
city = st.sidebar.multiselect("도시 선택(복수 가능)",df_state["City"].unique())

if not city:
    df_city = df_state.copy()
else:
    df_city = df_state[df_state["City"].isin(city)]

# 지역, 주, 도시에 따라 데이터프레임 필터링
filtered_df = df_city

# 카테고리별 판매액 계산
category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

# 각 컬럼에 대한 그래프 생성
with col1:
    st.subheader("제품 카테고리별 판매액")
    fig = px.bar(
        category_df, 
        x = "Category", y = "Sales", 
        text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],        template = "seaborn"
        )
    st.plotly_chart(fig, use_container_width=True, height = 200)

with col2:
    st.subheader("지역별 판매액")
    fig = px.pie(
        filtered_df, 
        values = "Sales", 
        names = "Region", 
        hole = 0.5
        )
    fig.update_traces(
        text = filtered_df["Region"], 
        textposition = "outside"
        )
    st.plotly_chart(fig,use_container_width=True)

# 화면을 2개의 컬럼으로 나누기
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("카테고리별 데이터 보기"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button(
            "데이터 다운로드", 
            data = csv, 
            file_name = "Category.csv", 
            mime = "text/csv",
            help = 'CSV 파일로 데이터를 다운로드하기 위해 클릭하세요.'
            )

with cl2:
    with st.expander("지역별 데이터 보기"):
        region = filtered_df.groupby(
            by = "Region", 
            as_index = False
            )["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button(
            "데이터 다운로드", 
            data = csv, 
            file_name = "Region.csv", 
            mime = "text/csv",
            help = 'CSV 파일로 데이터를 다운로드하기 위해 클릭하세요.'
            )


# 시계열 데이터 분석
st.subheader('시계열 분석')

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

linechart = pd.DataFrame(
    filtered_df.groupby(
        filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
        ).reset_index()
fig2 = px.line(
    linechart, 
    x = "month_year", y="Sales", 
    labels = {"Sales": "Amount"},
    height=500, width=1000,
    template="gridon"
    )
st.plotly_chart(fig2,use_container_width=True)

# 데이터 보기
with st.expander("시계열 데이터 보기:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# 트리맵을 이용한 판매 데이터 시각화

st.subheader("트리맵을 이용한 판매 데이터 시각화")

fig3 = px.treemap(
    filtered_df, 
    path = ["Region","Category","Sub-Category"], 
    values = "Sales",
    hover_data = ["Sales"],
    color = "Sub-Category"
    )
fig3.update_layout(width = 800, height = 650)

st.plotly_chart(fig3, use_container_width=True)

# 세그먼트별 판매 데이터 시각화
chart1, chart2 = st.columns((2))

with chart1:
    st.subheader('세그먼트별 판매')
    fig = px.pie(
        filtered_df, 
        values = "Sales", 
        names = "Segment", 
        template = "plotly_dark"
        )
    fig.update_traces(
        text = filtered_df["Segment"], 
        textposition = "inside"
        )
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('카테고리별 판매')
    fig = px.pie(
        filtered_df, 
        values = "Sales", 
        names = "Category", 
        template = "gridon"
        )
    fig.update_traces(
        text = filtered_df["Category"], 
        textposition = "inside"
        )
    st.plotly_chart(fig,use_container_width=True)

# 데이터 정리 테이블 시각화
import plotly.figure_factory as ff

st.subheader(":point_right: 월별 서브카테고리 판매 요약")

with st.expander("요약표"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(
        df_sample, 
        colorscale = "Cividis"
        )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("월별 서브카테고리 테이블")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(
        data = filtered_df, 
        values = "Sales", 
        index = ["Sub-Category"],
        columns = "month"
        )
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# 산점도를 이용한 판매와 이익의 관계 시각화
data1 = px.scatter(
    filtered_df, 
    x = "Sales", 
    y = "Profit", 
    size = "Quantity"
    )
data1['layout'].update(
    title="Relationship between Sales and Profits using Scatter Plot.",     titlefont = dict(size=20),
    xaxis = dict(title="Sales",titlefont=dict(size=19)),                      yaxis = dict(title = "Profit", titlefont = dict(size=19))
    )
st.plotly_chart(data1,use_container_width=True)

# 데이터 보기
with st.expander("데이터 보기"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# 데이터 다운로드
csv = df.to_csv(index = False).encode('utf-8')
st.download_button(
    'Download Data', 
    data = csv, 
    file_name = "Data.csv",
    mime = "text/csv"
    )