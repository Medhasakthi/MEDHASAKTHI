"""
Certificate Watermark Service for MEDHASAKTHI
Handles logo watermark functionality with proper positioning and transparency
"""
import os
import base64
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
import requests


class CertificateWatermarkService:
    """Service for managing certificate watermarks and logo placement"""
    
    def __init__(self):
        self.logo_cache = {}
        self.default_watermark_settings = {
            "opacity": 0.15,
            "position": "center",
            "size_ratio": 0.3,  # 30% of certificate width
            "rotation": -15,
            "blend_mode": "multiply"
        }
    
    def load_medhasakthi_logo(self, logo_path: Optional[str] = None) -> Optional[Image.Image]:
        """Load MEDHASAKTHI logo from file or URL"""
        try:
            if logo_path:
                if logo_path.startswith(('http://', 'https://')):
                    # Load from URL
                    response = requests.get(logo_path, timeout=10)
                    response.raise_for_status()
                    logo_image = Image.open(BytesIO(response.content))
                else:
                    # Load from local file
                    logo_image = Image.open(logo_path)
            else:
                # Use default logo path
                default_logo_path = os.path.join(
                    os.path.dirname(__file__), 
                    "..", "..", "assets", "images", "medhasakthi.png"
                )
                if os.path.exists(default_logo_path):
                    logo_image = Image.open(default_logo_path)
                else:
                    # Create a placeholder logo if file doesn't exist
                    logo_image = self._create_placeholder_logo()
            
            # Ensure logo has transparency
            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')
            
            return logo_image
            
        except Exception as e:
            print(f"Error loading MEDHASAKTHI logo: {str(e)}")
            return self._create_placeholder_logo()
    
    def _create_placeholder_logo(self) -> Image.Image:
        """Create a placeholder MEDHASAKTHI logo"""
        # Create a 200x200 placeholder with shield and text
        logo = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        
        # Draw shield shape
        shield_color = (184, 134, 11, 255)  # Golden color
        shield_points = [
            (100, 20), (140, 40), (160, 80), (160, 120),
            (140, 160), (100, 180), (60, 160), (40, 120),
            (40, 80), (60, 40)
        ]
        draw.polygon(shield_points, fill=shield_color)
        
        # Draw brain/circuit pattern (simplified)
        circuit_color = (139, 69, 19, 255)  # Brown color
        draw.ellipse([70, 60, 130, 120], outline=circuit_color, width=3)
        draw.line([85, 75, 115, 75], fill=circuit_color, width=2)
        draw.line([85, 90, 115, 90], fill=circuit_color, width=2)
        draw.line([85, 105, 115, 105], fill=circuit_color, width=2)
        
        # Add small circuits
        draw.rectangle([75, 70, 80, 75], fill=circuit_color)
        draw.rectangle([120, 70, 125, 75], fill=circuit_color)
        draw.rectangle([75, 100, 80, 105], fill=circuit_color)
        draw.rectangle([120, 100, 125, 105], fill=circuit_color)
        
        return logo
    
    def apply_watermark(
        self,
        certificate_image: Image.Image,
        watermark_settings: Optional[Dict[str, Any]] = None,
        logo_path: Optional[str] = None
    ) -> Image.Image:
        """Apply MEDHASAKTHI logo watermark to certificate"""
        
        # Merge settings with defaults
        settings = self.default_watermark_settings.copy()
        if watermark_settings:
            settings.update(watermark_settings)
        
        # Load logo
        logo = self.load_medhasakthi_logo(logo_path)
        if not logo:
            return certificate_image
        
        # Calculate watermark size and position
        cert_width, cert_height = certificate_image.size
        watermark_size = self._calculate_watermark_size(cert_width, cert_height, settings)
        watermark_position = self._calculate_watermark_position(
            cert_width, cert_height, watermark_size, settings
        )
        
        # Resize logo to watermark size
        logo_resized = logo.resize(watermark_size, Image.Resampling.LANCZOS)
        
        # Apply rotation if specified
        if settings.get("rotation", 0) != 0:
            logo_resized = logo_resized.rotate(
                settings["rotation"], 
                expand=True, 
                fillcolor=(0, 0, 0, 0)
            )
        
        # Apply opacity
        logo_with_opacity = self._apply_opacity(logo_resized, settings["opacity"])
        
        # Create watermark layer
        watermark_layer = Image.new('RGBA', certificate_image.size, (0, 0, 0, 0))
        watermark_layer.paste(logo_with_opacity, watermark_position, logo_with_opacity)
        
        # Composite watermark onto certificate
        if certificate_image.mode != 'RGBA':
            certificate_image = certificate_image.convert('RGBA')
        
        watermarked = Image.alpha_composite(certificate_image, watermark_layer)
        
        return watermarked
    
    def apply_corner_logo(
        self,
        certificate_image: Image.Image,
        logo_settings: Optional[Dict[str, Any]] = None,
        logo_path: Optional[str] = None
    ) -> Image.Image:
        """Apply MEDHASAKTHI logo to corner of certificate (non-watermark)"""
        
        # Default corner logo settings
        default_settings = {
            "position": "top_left",
            "size": (80, 80),
            "margin": (20, 20),
            "opacity": 1.0
        }
        
        settings = default_settings.copy()
        if logo_settings:
            settings.update(logo_settings)
        
        # Load logo
        logo = self.load_medhasakthi_logo(logo_path)
        if not logo:
            return certificate_image
        
        # Resize logo
        logo_resized = logo.resize(settings["size"], Image.Resampling.LANCZOS)
        
        # Apply opacity if needed
        if settings["opacity"] < 1.0:
            logo_resized = self._apply_opacity(logo_resized, settings["opacity"])
        
        # Calculate position
        position = self._calculate_corner_position(
            certificate_image.size, 
            settings["size"], 
            settings["position"], 
            settings["margin"]
        )
        
        # Apply logo to certificate
        if certificate_image.mode != 'RGBA':
            certificate_image = certificate_image.convert('RGBA')
        
        # Create a copy to avoid modifying original
        result = certificate_image.copy()
        result.paste(logo_resized, position, logo_resized)
        
        return result
    
    def _calculate_watermark_size(
        self, 
        cert_width: int, 
        cert_height: int, 
        settings: Dict[str, Any]
    ) -> Tuple[int, int]:
        """Calculate watermark size based on certificate dimensions"""
        
        size_ratio = settings.get("size_ratio", 0.3)
        
        # Use the smaller dimension to maintain aspect ratio
        base_size = min(cert_width, cert_height) * size_ratio
        
        # Maintain aspect ratio of logo (assuming square for placeholder)
        watermark_width = int(base_size)
        watermark_height = int(base_size)
        
        return (watermark_width, watermark_height)
    
    def _calculate_watermark_position(
        self,
        cert_width: int,
        cert_height: int,
        watermark_size: Tuple[int, int],
        settings: Dict[str, Any]
    ) -> Tuple[int, int]:
        """Calculate watermark position"""
        
        watermark_width, watermark_height = watermark_size
        position_type = settings.get("position", "center")
        
        if position_type == "center":
            x = (cert_width - watermark_width) // 2
            y = (cert_height - watermark_height) // 2
        elif position_type == "bottom_right":
            x = cert_width - watermark_width - 50
            y = cert_height - watermark_height - 50
        elif position_type == "top_left":
            x = 50
            y = 50
        elif position_type == "top_right":
            x = cert_width - watermark_width - 50
            y = 50
        elif position_type == "bottom_left":
            x = 50
            y = cert_height - watermark_height - 50
        else:
            # Default to center
            x = (cert_width - watermark_width) // 2
            y = (cert_height - watermark_height) // 2
        
        return (x, y)
    
    def _calculate_corner_position(
        self,
        cert_size: Tuple[int, int],
        logo_size: Tuple[int, int],
        position: str,
        margin: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Calculate corner logo position"""
        
        cert_width, cert_height = cert_size
        logo_width, logo_height = logo_size
        margin_x, margin_y = margin
        
        if position == "top_left":
            return (margin_x, margin_y)
        elif position == "top_right":
            return (cert_width - logo_width - margin_x, margin_y)
        elif position == "bottom_left":
            return (margin_x, cert_height - logo_height - margin_y)
        elif position == "bottom_right":
            return (cert_width - logo_width - margin_x, cert_height - logo_height - margin_y)
        else:
            # Default to top_left
            return (margin_x, margin_y)
    
    def _apply_opacity(self, image: Image.Image, opacity: float) -> Image.Image:
        """Apply opacity to image"""
        if opacity >= 1.0:
            return image
        
        # Create a copy and adjust alpha channel
        image_with_opacity = image.copy()
        
        if image_with_opacity.mode != 'RGBA':
            image_with_opacity = image_with_opacity.convert('RGBA')
        
        # Get alpha channel and multiply by opacity
        alpha = image_with_opacity.split()[-1]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        
        # Replace alpha channel
        image_with_opacity.putalpha(alpha)
        
        return image_with_opacity
    
    def create_verification_qr(
        self,
        verification_code: str,
        verification_url: str,
        size: Tuple[int, int] = (100, 100)
    ) -> Image.Image:
        """Create QR code for certificate verification"""
        try:
            import qrcode
            
            # Create QR code with verification URL
            qr_data = f"{verification_url}?code={verification_code}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize(size, Image.Resampling.LANCZOS)
            
            return qr_image
            
        except ImportError:
            # Create placeholder QR code if qrcode library not available
            qr_placeholder = Image.new('RGB', size, 'white')
            draw = ImageDraw.Draw(qr_placeholder)
            
            # Draw simple grid pattern
            grid_size = size[0] // 10
            for i in range(0, size[0], grid_size * 2):
                for j in range(0, size[1], grid_size * 2):
                    draw.rectangle([i, j, i + grid_size, j + grid_size], fill='black')
            
            return qr_placeholder


# Initialize global watermark service
certificate_watermark_service = CertificateWatermarkService()
