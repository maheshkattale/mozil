
from .models import *
from rest_framework import serializers

class AdvertisementsMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= AdvertisementsMaster
        fields='__all__'

class CustomAdvertisementsMasterSerializer(serializers.ModelSerializer):
    formatted_start_date = serializers.SerializerMethodField()
    formatted_end_date = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = AdvertisementsMaster
        fields = '__all__'
        extra_fields = ['formatted_start_date', 'formatted_end_date', 'media_url']

    def get_formatted_start_date(self, obj):
        """Convert stored date string to dd-mm-yyyy format"""
        if not obj.start_date:
            return None
        try:
            if '-' in obj.start_date:
                parts = obj.start_date.split('-')
                if len(parts[0]) == 4:  # yyyy-mm-dd format
                    year, month, day = parts
                    return f"{day}-{month}-{year}"
                elif len(parts[0]) == 2:  # dd-mm-yyyy format
                    return obj.start_date
        except:
            return obj.start_date
        return obj.start_date

    def get_formatted_end_date(self, obj):
        """Convert stored date string to dd-mm-yyyy format"""
        if not obj.end_date:
            return None
        try:
            if '-' in obj.end_date:
                parts = obj.end_date.split('-')
                if len(parts[0]) == 4:  # yyyy-mm-dd format
                    year, month, day = parts
                    return f"{day}-{month}-{year}"
                elif len(parts[0]) == 2:  # dd-mm-yyyy format
                    return obj.end_date
        except:
            return obj.end_date
        return obj.end_date

    def get_media_url(self, obj):
        if obj.media:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.media.url)
            return obj.media.url  # Fallback to relative URL if no request in context
        return None

    def to_internal_value(self, data):
        """Convert incoming dd-mm-yyyy dates to yyyy-mm-dd for storage"""
        data = super().to_internal_value(data)
        
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            if field in data and data[field]:
                try:
                    if '-' in data[field]:
                        parts = data[field].split('-')
                        if len(parts[0]) == 2:  # dd-mm-yyyy format
                            day, month, year = parts
                            data[field] = f"{year}-{month}-{day}"
                        # else assume it's already in yyyy-mm-dd format
                except (ValueError, AttributeError):
                    raise serializers.ValidationError({
                        field: "Date must be in dd-mm-yyyy format"
                    })
        return data