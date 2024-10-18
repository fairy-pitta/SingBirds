from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 他のURLパターン
    path('admin/', admin.site.urls),
    path('api/', include('singbirds.urls'))
]

# メディアファイル用のURLパターンを追加
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )