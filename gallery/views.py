from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .services.azure_toiletlabel import AzureToiletLabelService
from .services.azure_blob import upload_image
import uuid

azure_service = AzureToiletLabelService()

def upload_label(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return render(request, '403.html', status=403)
    if request.method == 'POST':
        place = request.POST['place']
        description = request.POST['description']
        men_image = request.FILES['men_image']
        women_image = request.FILES['women_image']
        label_id = str(uuid.uuid4())
        # Upload images to Azure Blob Storage
        import os
        men_ext = os.path.splitext(men_image.name)[1]
        women_ext = os.path.splitext(women_image.name)[1]
        men_filename = f"{label_id}_men{men_ext}"
        women_filename = f"{label_id}_women{women_ext}"
        men_url = upload_image(men_image, 'toiletlabels', men_filename)
        women_url = upload_image(women_image, 'toiletlabels', women_filename)
        # Store only the filenames in Azure Table
        azure_service.upsert_label(
            label_id=label_id,
            place=place,
            description=description,
            men_image_url=men_filename,
            women_image_url=women_filename,
            num_voters=0,
            avg_vote=0,
        )
        return redirect(reverse('gallery:signpair_list'))
    return render(request, 'gallery/upload_label.html')

def get_blob_base_url():
    import os
    import re
    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
    match = re.search(r"AccountName=([^;]+)", conn_str)
    account = match.group(1) if match else ""
    if account:
        return f"https://{account}.blob.core.windows.net/toiletlabels/"
    return ""

def signpair_list(request):
    pairs = azure_service.list_labels()
    return render(request, 'gallery/signpair_list.html', {
        'pairs': pairs,
        'AZURE_BLOB_BASE_URL': get_blob_base_url(),
    })

def signpair_detail(request, pk):
    pair = azure_service.get_label(pk)
    if not pair:
        return render(request, '404.html', status=404)
    return render(request, 'gallery/signpair_detail.html', {
        'pair': pair,
        'AZURE_BLOB_BASE_URL': get_blob_base_url(),
    })

def vote_view(request, pk):
    pair = azure_service.get_label(pk)
    if not pair:
        return render(request, '404.html', status=404)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        num_voters = pair.get('NumVoters', 0) or 0
        avg_vote = pair.get('AvgVote', 0) or 0
        # Update average
        new_avg = ((avg_vote * num_voters) + rating) / (num_voters + 1)
        azure_service.upsert_label(
            label_id=pk,
            place=pair['Place'],
            description=pair['Description'],
            men_image_url=pair['MenImageUrl'],
            women_image_url=pair['WomenImageUrl'],
            num_voters=num_voters + 1,
            avg_vote=new_avg,
        )
        return redirect(reverse('gallery:signpair_detail', args=[pk]))
    return redirect(reverse('gallery:signpair_detail', args=[pk]))
