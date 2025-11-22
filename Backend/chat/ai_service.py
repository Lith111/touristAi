import openai
import json
from django.conf import settings
from django.core.cache import cache
from packages.models import Destination, Service, Package

class AITravelAssistant:
    def __init__(self):
        # في الإصدار الحقيقي، سيتم استخدام API keys
        # هنا نستخدم محاكاة للذكاء الاصطناعي
        self.model_name = getattr(settings, 'AI_MODEL_NAME', 'travel-assistant')
        
    def generate_response(self, conversation_history, user_requirements):
        """توليد رد الذكاء الاصطناعي بناءً على سجل المحادثة والمتطلبات"""
        
        # محاكاة استجابة الذكاء الاصطناعي
        response_template = {
            "message": "",
            "action": "continue",  # continue, ask_clarification, generate_plan
            "missing_info": [],
            "suggestions": []
        }
        
        # تحليل المتطلبات الحالية
        current_requirements = self._analyze_requirements(user_requirements)
        missing_info = self._check_missing_info(current_requirements)
        
        if missing_info:
            response_template["action"] = "ask_clarification"
            response_template["missing_info"] = missing_info
            response_template["message"] = self._generate_clarification_message(missing_info)
        else:
            response_template["action"] = "generate_plan"
            response_template["message"] = "ممتاز! لدي كل المعلومات التي أحتاجها. سأقوم بإعداد خطة رحلتك المخصصة."
        
        # إضافة اقتراحات بناءً على المتطلبات
        response_template["suggestions"] = self._generate_suggestions(current_requirements)
        
        return response_template
    
    def _analyze_requirements(self, requirements):
        """تحليل متطلبات المستخدم"""
        analyzed = {
            "budget": requirements.get("budget", {}),
            "duration": requirements.get("duration_days"),
            "travelers": requirements.get("number_of_travelers", 1),
            "preferences": requirements.get("preferences", {}),
            "interests": requirements.get("interests", []),
            "constraints": requirements.get("constraints", [])
        }
        return analyzed
    
    def _check_missing_info(self, requirements):
        """التحقق من المعلومات المفقودة"""
        missing = []
        
        if not requirements.get("duration"):
            missing.append("duration")
        if not requirements.get("budget", {}).get("total"):
            missing.append("budget")
        if not requirements.get("preferences", {}).get("accommodation_level"):
            missing.append("accommodation_preference")
        if not requirements.get("interests"):
            missing.append("interests")
            
        return missing
    
    def _generate_clarification_message(self, missing_info):
        """توليد رسالة طلب توضيح"""
        messages = {
            "duration": "كم يوماً تخطط للبقاء؟",
            "budget": "ما هي ميزانيتك التقريبية للرحلة؟",
            "accommodation_preference": "ما مستوى الإقامة الذي تفضله؟ (اقتصادي، قياسي، فاخر)",
            "interests": "ما هي اهتماماتك؟ (تاريخية، طبيعية، ترفيهية، ثقافية)"
        }
        
        clarification_questions = [messages[info] for info in missing_info if info in messages]
        return "أحتاج إلى بعض المعلومات الإضافية لتخطيط رحلتك:\n" + "\n".join(f"• {q}" for q in clarification_questions)
    
    def _generate_suggestions(self, requirements):
        """توليد اقتراحات بناءً على المتطلبات"""
        suggestions = []
        
        # اقتراح وجهات بناءً على الاهتمامات
        interests = requirements.get("interests", [])
        if interests:
            destinations = Destination.objects.filter(is_active=True)
            for interest in interests:
                matching_destinations = destinations.filter(description__icontains=interest)[:2]
                for dest in matching_destinations:
                    suggestions.append(f"اقتراح: {dest.name} - {dest.description[:100]}...")
        
        return suggestions[:3]  # إرجاع 3 اقتراحات كحد أقصى
    
    def generate_travel_plan(self, requirements):
        """توليد خطة سفر مخصصة"""
        budget = requirements.get("budget", {}).get("total", 1000)
        duration = requirements.get("duration_days", 3)
        travelers = requirements.get("number_of_travelers", 1)
        
        # محاكاة توليد خطة سفر
        plan = {
            "summary": f"رحلة مخصصة لمدة {duration} أيام لمجموعة من {travelers} أشخاص",
            "total_estimated_cost": budget,
            "daily_plan": {},
            "included_services": [],
            "recommended_destinations": []
        }
        
        # توليد الخطة اليومية
        for day in range(1, duration + 1):
            plan["daily_plan"][f"day_{day}"] = {
                "morning": f"نشاط صباحي في اليوم {day}",
                "afternoon": f"نشاط بعد الظهر في اليوم {day}",
                "evening": f"نشاط مسائي في اليوم {day}"
            }
        
        return plan