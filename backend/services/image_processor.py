from PIL import Image
import os


class ImageProcessor:
    """
    Handles image processing and validation.
    """
    
    def __init__(self, max_size: tuple = (1024, 1024)):
        """
        Initialize image processor.
        
        Args:
            max_size: Maximum dimensions for image resize
        """
        self.max_size = max_size
    
    def validate_image(self, filepath: str) -> bool:
        """
        Validate if file is a valid image.
        
        Args:
            filepath: Path to the image file
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            with Image.open(filepath) as img:
                img.verify()
            return True
        except Exception as e:
            print(f"Image validation failed: {str(e)}")
            return False
    
    def get_image_info(self, filepath: str) -> dict:
        """
        Extract image metadata.
        
        Args:
            filepath: Path to the image file
            
        Returns:
            Dictionary containing image info
        """
        try:
            with Image.open(filepath) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
        except Exception as e:
            print(f"Error getting image info: {str(e)}")
            return {}
    
    def resize_image(self, filepath: str, output_path: str = None) -> str:
        """
        Resize image to max_size while maintaining aspect ratio.
        
        Args:
            filepath: Path to the input image
            output_path: Path for output image (optional)
            
        Returns:
            Path to resized image
        """
        try:
            if output_path is None:
                base, ext = os.path.splitext(filepath)
                output_path = f"{base}_resized{ext}"
            
            with Image.open(filepath) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Resize maintaining aspect ratio
                img.thumbnail(self.max_size, Image.Resampling.LANCZOS)
                
                # Save resized image
                img.save(output_path, quality=85, optimize=True)
            
            return output_path
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return filepath
    
    def analyze_image_content(self, filepath: str) -> str:
        """
        Basic image analysis (can be enhanced with ML models).
        
        Args:
            filepath: Path to the image file
            
        Returns:
            Description of image characteristics
        """
        try:
            info = self.get_image_info(filepath)
            
            # Determine orientation
            if info['width'] > info['height']:
                orientation = "landscape"
            elif info['width'] < info['height']:
                orientation = "portrait"
            else:
                orientation = "square"
            
            # Determine if high resolution
            total_pixels = info['width'] * info['height']
            quality = "high-resolution" if total_pixels > 1000000 else "standard-resolution"
            
            return f"{orientation} {quality} {info['format']} image"
            
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return "image"
    
    def read_text_file(self, filepath: str) -> str:
        """
        Read content from text file.
        
        Args:
            filepath: Path to text file
            
        Returns:
            Text content
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content.strip()
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            raise Exception(f"Failed to read text file: {str(e)}")