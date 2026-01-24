# views/attraction_view.py
from views.common_view import CommonView

class AttractionView:
    """處理景點相關的回應格式"""
    
    @staticmethod
    def format_attraction_list(search_data, images_dict, next_page):
        """格式化景點列表回應"""
        data = []
        for attraction in search_data:
            attraction_id = attraction[0]
            images = images_dict.get(attraction_id, [])
            
            attraction_dict = {
                "id": attraction[0],
                "name": attraction[1],
                "category": attraction[2],
                "description": attraction[3],
                "address": attraction[4],
                "transport": attraction[5],
                "mrt": attraction[6],
                "lat": attraction[7],
                "lng": attraction[8],
                "images": images
            }
            data.append(attraction_dict)
        
        return {
            "nextPage": next_page,
            "data": data
        }
    
    @staticmethod
    def format_attraction_detail(attraction, images):
        """格式化單一景點回應"""
        data = {
            "id": attraction[0],
            "name": attraction[1],
            "category": attraction[2],
            "description": attraction[3],
            "address": attraction[4],
            "transport": attraction[5],
            "mrt": attraction[6],
            "lat": attraction[7],
            "lng": attraction[8],
            "images": images
        }
        
        return {"data": data}
    
    @staticmethod
    def format_attraction_not_found():
        """格式化景點不存在回應"""
        return CommonView.format_error("景點編號不正確")
    
    @staticmethod
    def format_categories(categories):
        """格式化分類列表回應"""
        return {"data": categories}
    
    @staticmethod
    def format_mrts(mrts):
        """格式化捷運站列表回應"""
        return {"data": mrts}
