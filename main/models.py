from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SourceName(models.TextChoices):
    UNKNOWN = 'unkn', "Unknown"
    EBAY = 'ebay', "eBay"
    AMAZON = 'amzn', "Amazon"
    ALIEXPRESS = 'alix', "AliExpress"
    WILDBERRIES = 'wbrs', 'WildBerries'


class Seller(models.Model):
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=4, choices=SourceName.choices, default=SourceName.UNKNOWN)
    profile_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ("name", "source")

    def __str__(self):
        return f"{self.name} ({self.source})"

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    styled_name = models.CharField(max_length=512, null=True, blank=True)


class Item(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    options = models.JSONField(default=dict)
    link = models.URLField(max_length=2048)
    source = models.CharField(max_length=4, choices=SourceName.choices, default=SourceName.UNKNOWN)
    external_id = models.CharField(
        max_length=255,
        default='000',
        help_text="Unique identifier from the source platform (e.g. ASIN for Amazon, item number for eBay).",
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="items")
    
    # Commented temporary for migration purpose
    # class Meta:
        # unique_together = ("source", "external_id")
        
    def __str__(self):
        return self.name


class Fee(models.Model):
    class FeeType(models.IntegerChoices):
        SHIPPING = 1, "Shipping"
        TAX = 2, "Tax"
        IMPORT = 3, "Import Duty"
        SERVICE = 4, "Service Fee"
        OTHER = 5, "Other"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="fees")
    fee_type = models.SmallIntegerField(choices=FeeType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    country = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.fee_type} — {self.amount} {self.currency}"


class RecordedData(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="records")
    recorded_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discount percentage (e.g. 15.00 means 15%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    rating_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of users who submitted a rating",
    )

    class Meta:
        ordering = ["-recorded_at"]
        get_latest_by = "recorded_at"

    def __str__(self):
        return f"{self.item.name} @ {self.price} {self.currency} ({self.recorded_at:%Y-%m-%d %H:%M})"


class ItemMedia(models.Model):
    class MediaType(models.IntegerChoices):
        IMAGE = 0, "Image"
        VIDEO = 1, "Video"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="media")
    media_type = models.SmallIntegerField(choices=MediaType.choices, default=MediaType.IMAGE)
    file = models.FileField(upload_to="item_media/%Y/%m/", blank=True, null=True)
    url = models.URLField(max_length=2048, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "uploaded_at"]

    def __str__(self):
        return f"{self.media_type} for {self.item.name}"