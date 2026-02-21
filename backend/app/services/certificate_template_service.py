"""
Certificate Template Service for MEDHASAKTHI
Manages profession-specific certificate templates with proper layouts and designs
"""
from typing import Dict, Any, List, Optional
from app.models.certificate import ProfessionCategory, CertificateType


class CertificateTemplateService:
    """Service for managing certificate templates"""
    
    def __init__(self):
        self.profession_templates = self._initialize_profession_templates()
        self.default_settings = self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default template settings"""
        return {
            "dimensions": {
                "width": 1200,
                "height": 850,
                "dpi": 300
            },
            "orientation": "landscape",
            "fonts": {
                "title": {
                    "family": "Times New Roman",
                    "size": 36,
                    "weight": "bold",
                    "color": "#1a365d"
                },
                "subtitle": {
                    "family": "Arial",
                    "size": 24,
                    "weight": "normal",
                    "color": "#2d3748"
                },
                "body": {
                    "family": "Arial",
                    "size": 18,
                    "weight": "normal",
                    "color": "#4a5568"
                },
                "signature": {
                    "family": "Brush Script MT",
                    "size": 20,
                    "weight": "normal",
                    "color": "#1a365d"
                }
            },
            "colors": {
                "primary": "#1a365d",
                "secondary": "#2d3748",
                "accent": "#d69e2e",
                "background": "#ffffff",
                "border": "#e2e8f0"
            },
            "logo_position": {
                "x": 100,
                "y": 50,
                "width": 80,
                "height": 80
            },
            "watermark_settings": {
                "opacity": 0.1,
                "x": 400,
                "y": 300,
                "width": 400,
                "height": 250,
                "rotation": -15
            }
        }
    
    def _initialize_profession_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize profession-specific templates"""
        return {
            ProfessionCategory.INFORMATION_TECHNOLOGY: {
                "colors": {
                    "primary": "#0066cc",
                    "secondary": "#004499",
                    "accent": "#00aaff",
                    "background": "#f8fafc",
                    "border": "#0066cc"
                },
                "border_style": {
                    "type": "modern_tech",
                    "width": 8,
                    "pattern": "circuit_lines",
                    "corners": "rounded"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 150},
                    "content_area": {"x": 150, "y": 250, "width": 900, "height": 400},
                    "signature_area": {"x": 150, "y": 650, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "tech_pattern", "position": {"x": 50, "y": 200}},
                    {"type": "binary_code", "position": {"x": 1000, "y": 300}}
                ]
            },
            
            ProfessionCategory.HEALTHCARE: {
                "colors": {
                    "primary": "#dc2626",
                    "secondary": "#991b1b",
                    "accent": "#fbbf24",
                    "background": "#fefefe",
                    "border": "#dc2626"
                },
                "border_style": {
                    "type": "medical_cross",
                    "width": 6,
                    "pattern": "medical_symbols",
                    "corners": "classic"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 140},
                    "content_area": {"x": 150, "y": 240, "width": 900, "height": 420},
                    "signature_area": {"x": 150, "y": 660, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "medical_caduceus", "position": {"x": 50, "y": 180}},
                    {"type": "health_symbols", "position": {"x": 1000, "y": 280}}
                ]
            },
            
            ProfessionCategory.FINANCE_ACCOUNTING: {
                "colors": {
                    "primary": "#059669",
                    "secondary": "#047857",
                    "accent": "#d97706",
                    "background": "#f9fafb",
                    "border": "#059669"
                },
                "border_style": {
                    "type": "financial_elegant",
                    "width": 5,
                    "pattern": "currency_symbols",
                    "corners": "sharp"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 145},
                    "content_area": {"x": 150, "y": 245, "width": 900, "height": 410},
                    "signature_area": {"x": 150, "y": 655, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "financial_charts", "position": {"x": 50, "y": 190}},
                    {"type": "currency_pattern", "position": {"x": 1000, "y": 290}}
                ]
            },
            
            ProfessionCategory.ENGINEERING: {
                "colors": {
                    "primary": "#7c3aed",
                    "secondary": "#5b21b6",
                    "accent": "#f59e0b",
                    "background": "#fafafa",
                    "border": "#7c3aed"
                },
                "border_style": {
                    "type": "engineering_blueprint",
                    "width": 7,
                    "pattern": "gear_lines",
                    "corners": "technical"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 148},
                    "content_area": {"x": 150, "y": 248, "width": 900, "height": 404},
                    "signature_area": {"x": 150, "y": 652, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "engineering_tools", "position": {"x": 50, "y": 185}},
                    {"type": "blueprint_grid", "position": {"x": 1000, "y": 285}}
                ]
            },
            
            ProfessionCategory.MANAGEMENT: {
                "colors": {
                    "primary": "#1f2937",
                    "secondary": "#111827",
                    "accent": "#f59e0b",
                    "background": "#ffffff",
                    "border": "#1f2937"
                },
                "border_style": {
                    "type": "executive_formal",
                    "width": 4,
                    "pattern": "professional_lines",
                    "corners": "classic"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 142},
                    "content_area": {"x": 150, "y": 242, "width": 900, "height": 416},
                    "signature_area": {"x": 150, "y": 658, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "leadership_symbols", "position": {"x": 50, "y": 175}},
                    {"type": "corporate_pattern", "position": {"x": 1000, "y": 275}}
                ]
            },
            
            ProfessionCategory.CYBERSECURITY: {
                "colors": {
                    "primary": "#dc2626",
                    "secondary": "#991b1b",
                    "accent": "#fbbf24",
                    "background": "#0f172a",
                    "border": "#dc2626"
                },
                "border_style": {
                    "type": "security_shield",
                    "width": 6,
                    "pattern": "security_locks",
                    "corners": "fortified"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 145},
                    "content_area": {"x": 150, "y": 245, "width": 900, "height": 410},
                    "signature_area": {"x": 150, "y": 655, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "security_shields", "position": {"x": 50, "y": 180}},
                    {"type": "cyber_matrix", "position": {"x": 1000, "y": 280}}
                ]
            },
            
            ProfessionCategory.DATA_SCIENCE: {
                "colors": {
                    "primary": "#7c3aed",
                    "secondary": "#5b21b6",
                    "accent": "#06b6d4",
                    "background": "#f8fafc",
                    "border": "#7c3aed"
                },
                "border_style": {
                    "type": "data_analytics",
                    "width": 5,
                    "pattern": "data_points",
                    "corners": "analytical"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 147},
                    "content_area": {"x": 150, "y": 247, "width": 900, "height": 406},
                    "signature_area": {"x": 150, "y": 653, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "data_visualization", "position": {"x": 50, "y": 182}},
                    {"type": "algorithm_pattern", "position": {"x": 1000, "y": 282}}
                ]
            },
            
            ProfessionCategory.DIGITAL_MARKETING: {
                "colors": {
                    "primary": "#ec4899",
                    "secondary": "#be185d",
                    "accent": "#f59e0b",
                    "background": "#fefefe",
                    "border": "#ec4899"
                },
                "border_style": {
                    "type": "creative_modern",
                    "width": 6,
                    "pattern": "social_icons",
                    "corners": "trendy"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 144},
                    "content_area": {"x": 150, "y": 244, "width": 900, "height": 412},
                    "signature_area": {"x": 150, "y": 656, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "marketing_icons", "position": {"x": 50, "y": 177}},
                    {"type": "social_media_pattern", "position": {"x": 1000, "y": 277}}
                ]
            },
            
            ProfessionCategory.DESIGN_CREATIVE: {
                "colors": {
                    "primary": "#8b5cf6",
                    "secondary": "#7c3aed",
                    "accent": "#f59e0b",
                    "background": "#ffffff",
                    "border": "#8b5cf6"
                },
                "border_style": {
                    "type": "artistic_creative",
                    "width": 8,
                    "pattern": "creative_swirls",
                    "corners": "artistic"
                },
                "layout": {
                    "title_position": {"x": 600, "y": 146},
                    "content_area": {"x": 150, "y": 246, "width": 900, "height": 408},
                    "signature_area": {"x": 150, "y": 654, "width": 900, "height": 100}
                },
                "decorative_elements": [
                    {"type": "design_tools", "position": {"x": 50, "y": 179}},
                    {"type": "creative_palette", "position": {"x": 1000, "y": 279}}
                ]
            }
        }
    
    def get_template_for_profession(
        self, 
        profession_category: ProfessionCategory,
        certificate_type: CertificateType
    ) -> Dict[str, Any]:
        """Get template configuration for specific profession and certificate type"""
        
        # Get profession-specific template or default
        profession_template = self.profession_templates.get(
            profession_category, 
            self.profession_templates[ProfessionCategory.GENERAL] if ProfessionCategory.GENERAL in self.profession_templates else {}
        )
        
        # Start with default settings
        template = self.default_settings.copy()
        
        # Apply profession-specific overrides
        if profession_template:
            template.update(profession_template)
        
        # Apply certificate type specific modifications
        template = self._apply_certificate_type_modifications(template, certificate_type)
        
        return template
    
    def _apply_certificate_type_modifications(
        self, 
        template: Dict[str, Any], 
        certificate_type: CertificateType
    ) -> Dict[str, Any]:
        """Apply certificate type specific modifications"""
        
        if certificate_type == CertificateType.PROFESSIONAL:
            # Professional certificates get more formal styling
            template["fonts"]["title"]["size"] = 40
            template["border_style"]["width"] = template["border_style"].get("width", 5) + 2
            
        elif certificate_type == CertificateType.ACHIEVEMENT:
            # Achievement certificates get more celebratory styling
            template["colors"]["accent"] = "#fbbf24"  # Gold accent
            template["decorative_elements"].append({
                "type": "achievement_stars",
                "position": {"x": 500, "y": 100}
            })
            
        elif certificate_type == CertificateType.PARTICIPATION:
            # Participation certificates get simpler styling
            template["fonts"]["title"]["size"] = 32
            template["border_style"]["width"] = max(template["border_style"].get("width", 5) - 1, 3)
        
        return template
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of all available templates"""
        templates = []
        
        for profession in ProfessionCategory:
            for cert_type in CertificateType:
                template_config = self.get_template_for_profession(profession, cert_type)
                templates.append({
                    "profession_category": profession.value,
                    "certificate_type": cert_type.value,
                    "name": f"{profession.value.replace('_', ' ').title()} - {cert_type.value.replace('_', ' ').title()}",
                    "preview_config": template_config
                })
        
        return templates
    
    def validate_template_data(self, template_data: Dict[str, Any]) -> bool:
        """Validate template data structure"""
        required_fields = ["dimensions", "fonts", "colors", "layout"]
        
        for field in required_fields:
            if field not in template_data:
                return False
        
        # Validate dimensions
        if not all(key in template_data["dimensions"] for key in ["width", "height", "dpi"]):
            return False
        
        # Validate fonts
        if not all(key in template_data["fonts"] for key in ["title", "body"]):
            return False
        
        # Validate colors
        if not all(key in template_data["colors"] for key in ["primary", "background"]):
            return False
        
        return True


# Initialize global template service
certificate_template_service = CertificateTemplateService()
