from django.urls import path
from .views import chatbot_ui, query_deepseek_r1

urlpatterns = [
    path("", chatbot_ui, name="chatbot-ui"),  # Chatbot UI
    path("query/", query_deepseek_r1, name="query-deepseek"),  # API endpoint
]
