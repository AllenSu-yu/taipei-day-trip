# controllers/attraction_controller.py
from models.attraction_model import AttractionModel
from views.attraction_view import AttractionView
from views.common_view import CommonView

class AttractionController:
    """處理景點相關的請求"""
    
    @staticmethod
    def get_attractions(page, category=None, keyword=None):
        """取得景點列表"""
        try:
            search_data, images_dict, next_page = AttractionModel.get_attractions(page, category, keyword)
            return AttractionView.format_attraction_list(search_data, images_dict, next_page)
        except Exception as e:
            return CommonView.format_error(str(e))
    
    @staticmethod
    def get_attraction_by_id(attraction_id):
        """取得單一景點"""
        try:
            result = AttractionModel.get_attraction_by_id(attraction_id)
            
            if not result:
                return AttractionView.format_attraction_not_found()
            
            attraction, images = result
            return AttractionView.format_attraction_detail(attraction, images)
            
        except Exception as e:
            return CommonView.format_error(str(e))
    
    @staticmethod
    def get_categories():
        """取得所有分類"""
        try:
            categories = AttractionModel.get_categories()
            return AttractionView.format_categories(categories)
        except Exception as e:
            return CommonView.format_error(str(e))
    
    @staticmethod
    def get_mrts():
        """取得所有捷運站"""
        try:
            mrts = AttractionModel.get_mrts()
            return AttractionView.format_mrts(mrts)
        except Exception as e:
            return CommonView.format_error(str(e))
