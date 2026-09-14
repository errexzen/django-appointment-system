from django.views.generic import TemplateView


class LandingPageView(TemplateView):
    template_name = "web/landing.html"


class FeaturesPageView(TemplateView):
    template_name = "web/features.html"


class PricingPageView(TemplateView):
    template_name = "web/pricing.html"
