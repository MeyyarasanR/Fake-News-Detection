from fact_checker import verify_news


news = input(
    "Enter news: "
)


result = verify_news(
    news
)


print(result)