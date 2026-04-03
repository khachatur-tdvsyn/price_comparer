from django.contrib import admin, messages

from .models import Fee, Item, ItemMedia, RecordedData, Seller, Tag
from .tasks import get_ebay_homepage_results


class FeeInline(admin.TabularInline):
    model = Fee
    extra = 1


class RecordedDataInline(admin.TabularInline):
    model = RecordedData
    extra = 0
    readonly_fields = ("recorded_at",)


class ItemMediaInline(admin.TabularInline):
    model = ItemMedia
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "external_id", "seller", "created")
    list_filter = ("source", "seller", "tags")
    search_fields = ("name", "description", "link", "external_id")
    filter_horizontal = ("tags",)
    readonly_fields = ("created",)
    inlines = [FeeInline, RecordedDataInline, ItemMediaInline]
    actions = ['get_ebay_items']

    @admin.action(description="Get items from Ebay homepage")
    def get_ebay_items(self, request, queryset):
        task = get_ebay_homepage_results.delay()
        self.message_user(
            request,
            f"Request sent successfully wit task_id {task}",
            messages.SUCCESS,
        )


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "profile_url")
    list_filter = ("source",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(RecordedData)
class RecordedDataAdmin(admin.ModelAdmin):
    list_display = ("item", "price", "currency", "discount", "rating", "rating_count", "recorded_at")
    list_filter = ("currency",)
    search_fields = ("item__name",)
    readonly_fields = ("recorded_at",)


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ("item", "fee_type", "amount", "currency", "country")
    list_filter = ("fee_type", "currency", "country")
    search_fields = ("item__name", "country")


@admin.register(ItemMedia)
class ItemMediaAdmin(admin.ModelAdmin):
    list_display = ("item", "media_type", "is_primary", "uploaded_at")
    list_filter = ("media_type", "is_primary")
    search_fields = ("item__name", "alt_text")
    readonly_fields = ("uploaded_at",)

    