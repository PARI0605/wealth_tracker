import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from tracker.models import Asset, Liability
from tracker.forms import AssetForm, LiabilityForm
from tracker.services.wealth_service import get_net_worth_summary


@login_required
def net_worth_view(request):
    """
    Main Net Worth Dashboard:
    Renders asset/liability KPIs, Net Worth trajectory line chart,
    asset allocation donut, liability composition, and asset/liability tables.
    """
    summary = get_net_worth_summary(request.user)
    asset_form = AssetForm()
    liability_form = LiabilityForm()

    context = {
        'total_assets': summary['total_assets'],
        'total_liabilities': summary['total_liabilities'],
        'net_worth': summary['net_worth'],
        'debt_to_asset_ratio': summary['debt_to_asset_ratio'],
        'solvency': summary['solvency'],
        'assets': summary['assets'],
        'liabilities': summary['liabilities'],
        'asset_form': asset_form,
        'liability_form': liability_form,
        # JSON serialized data for Chart.js
        'asset_labels_json': json.dumps(summary['asset_labels']),
        'asset_data_json': json.dumps(summary['asset_data']),
        'asset_colors_json': json.dumps(summary['asset_colors']),
        'liability_labels_json': json.dumps(summary['liability_labels']),
        'liability_data_json': json.dumps(summary['liability_data']),
        'liability_colors_json': json.dumps(summary['liability_colors']),
        'trajectory_labels_json': json.dumps(summary['trajectory_labels']),
        'trajectory_data_json': json.dumps(summary['trajectory_data']),
    }
    return render(request, 'tracker/net_worth.html', context)


@login_required
def add_asset_view(request):
    """
    Adds a new asset record scoped to the authenticated user.
    """
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.user = request.user
            asset.save()
            messages.success(request, f"Asset '{asset.name}' of ₹{asset.amount} added to portfolio.")
            return redirect('net_worth')
    else:
        form = AssetForm()

    return render(request, 'tracker/add_asset.html', {'form': form})


@login_required
def edit_asset_view(request, pk: int):
    """
    Edits an existing asset with strict multi-tenant isolation.
    """
    asset = get_object_or_404(Asset, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f"Asset '{asset.name}' updated successfully.")
            return redirect('net_worth')
    else:
        form = AssetForm(instance=asset)

    return render(request, 'tracker/edit_asset.html', {'form': form, 'asset': asset})


@login_required
def delete_asset_view(request, pk: int):
    """
    Deletes an asset record belonging to the authenticated user.
    """
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    name = asset.name
    amount = asset.amount
    asset.delete()
    messages.success(request, f"Asset '{name}' (₹{amount}) removed from Net Worth portfolio.")
    return redirect('net_worth')


@login_required
def add_liability_view(request):
    """
    Adds a new liability or debt obligation scoped to the authenticated user.
    """
    if request.method == 'POST':
        form = LiabilityForm(request.POST)
        if form.is_valid():
            liability = form.save(commit=False)
            liability.user = request.user
            liability.save()
            messages.success(request, f"Liability '{liability.name}' of ₹{liability.amount} recorded.")
            return redirect('net_worth')
    else:
        form = LiabilityForm()

    return render(request, 'tracker/add_liability.html', {'form': form})


@login_required
def edit_liability_view(request, pk: int):
    """
    Edits an existing liability with strict multi-tenant isolation.
    """
    liability = get_object_or_404(Liability, pk=pk, user=request.user)

    if request.method == 'POST':
        form = LiabilityForm(request.POST, instance=liability)
        if form.is_valid():
            form.save()
            messages.success(request, f"Liability '{liability.name}' updated successfully.")
            return redirect('net_worth')
    else:
        form = LiabilityForm(instance=liability)

    return render(request, 'tracker/edit_liability.html', {'form': form, 'liability': liability})


@login_required
def delete_liability_view(request, pk: int):
    """
    Deletes a liability obligation belonging to the authenticated user.
    """
    liability = get_object_or_404(Liability, pk=pk, user=request.user)
    name = liability.name
    amount = liability.amount
    liability.delete()
    messages.success(request, f"Liability '{name}' (₹{amount}) removed.")
    return redirect('net_worth')
