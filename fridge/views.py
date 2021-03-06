import json
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from myblog.views import LoginRequiredMixin
from django.http import HttpResponseRedirect

from fridge.models import *
from rest_framework import viewsets
from fridge.serializers import IngredientSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# ShoppingMemoController
# shopping memo


class ShoppingList(View):
    # get_shopping_list
    def get(self, request):
        template_name = 'fridge/shopping_memo.html'
        owner = request.user
        # 쇼핑 리스트 가져오기
        shopping_list = ShoppingItem.get_shopping_item(owner)
        return render(request, template_name, {'meat': shopping_list['meat'],
                                               'seafood': shopping_list['seafood'],
                                               'fruit': shopping_list['fruit'],
                                               'grain': shopping_list['grain'],
                                               'milk': shopping_list['milk'],
                                               'made': shopping_list['made'],
                                               'side': shopping_list['side'],
                                               'drink': shopping_list['drink'],
                                               })

    # delete_item
    def post(self, request, pk):
        template_name = 'fridge/shopping_memo.html'
        owner = request.user
        shopping_list = ShoppingItem.get_shopping_item(owner)
        # 쇼핑 아이템 삭제하기
        ShoppingItem.delete_item(pk)
        return render(request, template_name, {'meat': shopping_list['meat'],
                                               'seafood': shopping_list['seafood'],
                                               'fruit': shopping_list['fruit'],
                                               'grain': shopping_list['grain'],
                                               'milk': shopping_list['milk'],
                                               'made': shopping_list['made'],
                                               'side': shopping_list['side'],
                                               'drink': shopping_list['drink'],
                                               })


# ShoppingMemoController
# class ShoppingItemDelete(LoginRequiredMixin, DeleteView):
#     model = ShoppingItem
#     success_url = reverse_lazy('fridge:shopping')


# FridgeManage Controller (냉장고 관리 페이지)
class FridgeManage(View):
    # get_uer_fridge_items
    def get(self, request):
        template_name = 'fridge/fridge_manage.html'
        owner = request.user
        fridge_items = FridgeItem.get_fridge_item(owner)
        return render(request, template_name, {'cold': fridge_items['cold'],
                                               'frozen': fridge_items['frozen'],
                                               'warm': fridge_items['warm']
                                               })

    # delete_fridge_item
    def post(self, request, pk):
        template_name = 'fridge/fridge_manage.html'
        owner = request.user
        fridge_items = FridgeItem.get_fridge_item(owner)
        FridgeItem.delete_item(pk)
        return render(request, template_name, {'cold': fridge_items['cold'],
                                               'frozen': fridge_items['frozen'],
                                               'warm': fridge_items['warm']
                                               })


# save_fridge_item in FridgeManage
class ItemSaver(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, format=None):
        print(request.data)
        try:
            data = request.data['ingredient_ids']
            data = json.loads(data)
            print(data)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'message': 'bad request, arguments error'})
        current_user = request.user
        print(data)
        for ingredient_id in data:
            ingredient = Ingredient.objects.filter(id=int(ingredient_id)).first()
            fridge_item = FridgeItem.objects.filter(owner=current_user, iteminfo=ingredient).first()
            if fridge_item:
                None
                
            else:
                new_fridge_item = FridgeItem(owner=current_user, iteminfo=ingredient)
                new_fridge_item.save()

        return JsonResponse({'code': 200, 'message': 'add success'})



# add_fridge_item (unsaved) in FridgeManage
class PostManager(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, format=None):
        # return render(request, tempalte_name, {'cold':fridge_items['warm']})
        ingredient_ids = json.loads(request.data['ingredient_ids'])
        print(ingredient_ids)
        ret = {}
        for ingredient_id in ingredient_ids:
            fridge_item = FridgeItem.objects.select_related("iteminfo").filter(
                iteminfo__ingredientCode=int(ingredient_id), owner=request.user)
            if fridge_item.first():
                fridge_item = fridge_item.first()
                if 'update_fridge_item' in ret:
                    ret['update_fridge_item'].append({
                        fridge_item.jsonify()
                    })
                else:
                    ret['update_fridge_item'] = [fridge_item.jsonify()]
            else:
                ingredient = Ingredient.objects.get(ingredientCode=int(ingredient_id))
                if 'new_fridge_item' in ret:
                    ret['new_fridge_item'].append(ingredient.jsonify())
                else:
                    ret['new_fridge_item'] = [ingredient.jsonify()]

        return JsonResponse({'code': 200, 'message': 'get success', 'data': ret})


# AddIngredient in FridgeManage page (냉장고 관리의 재료추가 페이지 )
class AddIngredientManage(TemplateView):
    template_name = 'fridge/addingredient_manage.html'

    def get_ingre(self):
        ingredient_type = int(self.request.GET.get('type') or '0')
        if ingredient_type == 0:
            ingredients = Ingredient.objects.all()
        else:
            ingredients = Ingredient.objects.filter(type=ingredient_type)
        context = {'ingredients': ingredients}
        return context


# AddIngredientController_1
class AddIngredient(TemplateView):
    template_name = 'fridge/addingredient_shopping.html'

    def get_ingre(self):
        ingredient_type = int(self.request.GET.get('type') or '0')
        if ingredient_type == 0:
            ingredients = Ingredient.objects.all()
        else:
            ingredients = Ingredient.objects.filter(type=ingredient_type)
        context = {'ingredients': ingredients}
        return context


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    lookup_field = 'type'

    def get_queryset(self):
        ingredient_type = int(self.request.GET.get('type') or '0')
        if ingredient_type == 0:
            ingredients = Ingredient.objects.all()
        else:
            ingredients = Ingredient.objects.filter(type=ingredient_type)

        queryset = ingredients
        return queryset


# AddIngredientController_2
# save ingredient in DB at shopping page
class SaveItemShopping(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, format=None):
        try:
            data = request.data['ingredient_ids']
            data = json.loads(data)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'message': 'bad request, arguments error'})
        current_user = request.user

        for ingredient_id in data:
            ingredient = Ingredient.objects.filter(ingredientCode=int(ingredient_id)).first()
            shopping_item = ShoppingItem.objects.filter(owner=current_user, iteminfo=ingredient).first()
            if shopping_item:
                None
            else:
                new_shopping_item = ShoppingItem(owner=current_user, iteminfo=ingredient)
                try:
                    new_shopping_item.save()
                except Exception as e:
                    return JsonResponse({'code': 500, "message": "error: database commit"})
        return JsonResponse({'code': 200, 'message': 'add success'})


class RecommendationList(View):
    # get recommendation list
    def get(self, request):
        template_name = 'fridge/recom_list.html'
        owner = request.user
        recommendation_list = Recommendation.get_recommendation(owner)
        fridge_items = FridgeItem.get_fridge_item(owner)

        return render(request, template_name, {'recom_list': recommendation_list,
                                                'cold': fridge_items['cold'],
                                               'frozen': fridge_items['frozen'],
                                               'warm': fridge_items['warm']
                                               })


class RecommendationDetail(View):
    # get recommendation recipe
    def get(self, request, pk):
        template_name = 'fridge/menu_detail.html'
        recom_menu = get_object_or_404(Menu, pk=pk)
        yes_ingre, no_ingre = Recommendation.has_what(request.user, pk)

        return render(request, template_name, {'menu': recom_menu,
                                               'yes_ingre': yes_ingre,
                                               'no_ingre': no_ingre})

    def post(self, request, pk):
        template_name = 'fridge/recom_list.html'
        recom_menu = get_object_or_404(Menu, pk=pk)
        yes_ingre, no_ingre = Recommendation.has_what(request.user, pk)
        return render(request, template_name, {'menu': recom_menu,
                                                'yes_ingre': yes_ingre,
                                                'no_ingre': no_ingre})
        

        # if no_ingre:
        #     return render(request, template_name, {'menu': recom_menu,
        #                                            'yes_ingre': yes_ingre,
        #                                            'no_ingre': no_ingre})
        # else:
        #     main_ingredients = recom_menu.main_ingredients
        #     sub_ingredients = recom_menu.sub_ingredients
        #     FridgeItem.use_fridge_item(request.user, main_ingredients, sub_ingredients)
        #     return HttpResponseRedirect(reverse('fridge:recommendation'))


class Scrap(View):
    def post(self, request, pk):
        ScrapList.add_scrap(request.user, pk)
        return HttpResponseRedirect(reverse('fridge:menu_detail', args=(pk,)))

    def get(self, request):
        template_name = 'fridge/scrap_list.html'
        owner = request.user
        scrap_list = ScrapList.scrap_menu(owner)
        return render(request, template_name, {'scraps': scrap_list})

class ScrapDetail(View):
        def post(self, request, pk):
            template_name = 'fridge/scrap_list.html'
            owner = request.user
            # 쇼핑 아이템 삭제하기
            ScrapList.delete_scrap_item(pk)
            scrap_list = ScrapList.scrap_menu(owner)
            return render(request, template_name, {'scraps': scrap_list})

class Home(TemplateView):
    template_name = 'home.html'

class Manage(TemplateView):
    template_name = 'fridge/manage.html'

