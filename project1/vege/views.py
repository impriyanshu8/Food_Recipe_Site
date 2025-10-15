from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from .models import Recipe
import os
from django.conf import settings

# Create your views here.
def recipe(request):
    if request.method == "POST":
        data = request.POST
        recipe_image = request.FILES.get('recipe_image')

        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')

        Recipe.objects.create(
            recipe_image = recipe_image,
            recipe_name = recipe_name,
            recipe_description = recipe_description
        )
        return redirect('/recipe/')

    queryset = Recipe.objects.all()

    if request.GET.get('search'):
        queryset = queryset.filter(recipe_name__icontains = request.GET.get('search'))
       

    context  = {'recipes': queryset}
  

    return render(request, 'recipe.html',context)

def update_recipe(request, id):
    queryset = Recipe.objects.get(id=id)

    if request.method == "POST":
        data = request.POST

        recipe_image = request.FILES.get('recipe_image')
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')

        queryset.recipe_name = recipe_name
        queryset.recipe_description = recipe_description

        if recipe_image:
            queryset.recipe_image = recipe_image

        queryset.save()
        return redirect('/recipe/')


    context = {'recipe': queryset}

    return render(request, 'update_recipes.html', context)

def delete_recipe(request, id):
    queryset = Recipe.objects.get(id = id)
    queryset.delete()
    return redirect('/recipe/')

def download_recipe_pdf(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    # Create the HTTP response with PDF header
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{recipe.recipe_name}.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Add content
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, recipe.recipe_name)

    p.setFont("Helvetica", 12)
    text_object = p.beginText(50, height - 100)
    for line in recipe.recipe_description.split('\n'):
        text_object.textLine(line)
    p.drawText(text_object)

    # Add Image (if available)
    if recipe.recipe_image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(recipe.recipe_image))
        if os.path.exists(image_path):
            p.drawImage(image_path, 50, 200, width=200, preserveAspectRatio=True)

    p.showPage()
    p.save()

    return response