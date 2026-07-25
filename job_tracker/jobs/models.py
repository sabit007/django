from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class JobApplication(models.Model):
    # --- Status choices ---
    # Using a tuple of (stored_value, human_readable_label).
    # The stored value is what goes in the DB; the label is what shows in forms/admin.
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (APPLIED, "Applied"),
        (INTERVIEW, "Interview"),
        (OFFER, "Offer"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    ]

    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_location = models.CharField(max_length=200)

    # Optional field -> blank=True (form validation) AND null=True (DB allows NULL)
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message="Salary cannot be negative.")],
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=APPLIED,
    )

    application_date = models.DateField()
    deadline = models.DateField()

    notes = models.TextField(blank=True, max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)  # set once, on creation
    updated_at = models.DateTimeField(auto_now=True)      # updated every save

    class Meta:
        ordering = ["-created_at"]  # newest first by default

    def __str__(self):
        return f"{self.position} @ {self.company_name}"

    def clean(self):
        """
        Model-level validation that doesn't fit neatly into a single field.
        This runs whenever the ModelForm calls full_clean(), so it protects
        the app even if someone adds another form/view later.
        """
        super().clean()
        if self.application_date and self.deadline:
            if self.deadline < self.application_date:
                raise ValidationError(
                    {"deadline": "Deadline cannot be earlier than the application date."}
                )
