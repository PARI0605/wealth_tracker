import io
import csv
import datetime
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Q

from tracker.models import Transaction, Category
from tracker.forms import TransactionForm, CategoryForm, CSVImportForm
from tracker.ai import predict_category, get_transaction_anomaly_ids



@login_required
def transaction_list_view(request):
    """
    Transaction ledger with advanced server-side filters, search,
    summary cards for filtered subset, and pagination.
    Strictly isolated to request.user.
    """
    qs = (
        Transaction.objects.filter(user=request.user)
        .select_related('category')
        .order_by('-date', '-created_at')
    )

    # 1. Search filter (description, category name, or payment method)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(description__icontains=q) |
            Q(category__name__icontains=q) |
            Q(payment_method__icontains=q)
        )

    # 2. Type filter (income / expense)
    type_filter = request.GET.get('type', '').strip().lower()
    if type_filter in ('income', 'expense'):
        qs = qs.filter(type=type_filter)

    # 3. Category filter
    category_id = request.GET.get('category', '').strip()
    if category_id:
        qs = qs.filter(category_id=category_id)

    # 4. Date range filters
    start_date = request.GET.get('start_date', '').strip()
    if start_date:
        try:
            qs = qs.filter(date__gte=start_date)
        except Exception:
            pass

    end_date = request.GET.get('end_date', '').strip()
    if end_date:
        try:
            qs = qs.filter(date__lte=end_date)
        except Exception:
            pass

    # Aggregates for the filtered dataset
    filtered_income = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    filtered_expense = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    filtered_net = filtered_income - filtered_expense

    # Pagination: 25 items per page
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user).order_by('name')
    anomaly_ids = get_transaction_anomaly_ids(request.user)

    context = {
        'page_obj': page_obj,
        'transactions': page_obj.object_list,
        'categories': categories,
        'total_count': qs.count(),
        'filtered_income': filtered_income,
        'filtered_expense': filtered_expense,
        'filtered_net': filtered_net,
        'anomaly_ids': anomaly_ids,
        # Active filter values for form preservation
        'q': q,
        'active_type': type_filter,
        'active_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'tracker/transaction_list.html', context)


@login_required
def add_transaction_view(request):
    """
    Record income or expense transaction.
    If category is left unselected, automatically assigns the prediction from
    the Naive Bayes NLP model.
    """
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user

            # AI Fallback: Auto-classify if category is unassigned
            if not transaction.category and transaction.description:
                _, _, matched_cat = predict_category(transaction.description, user=request.user)
                if matched_cat:
                    transaction.category = matched_cat

            transaction.save()
            messages.success(request, f"Recorded {transaction.type.title()} of ₹{transaction.amount} successfully.")
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)

    return render(request, 'tracker/add_transaction.html', {'form': form})


@login_required
def edit_transaction_view(request, pk: int):
    """
    Update an existing transaction record with strict tenant isolation.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Transaction #{pk} updated successfully.")
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(request, 'tracker/edit_transaction.html', {
        'form': form,
        'transaction': transaction
    })


@login_required
def delete_transaction_view(request, pk: int):
    """
    Permanently deletes a transaction record with strict user isolation.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    messages.success(request, "Transaction deleted successfully.")
    return redirect('transaction_list')


@login_required
def export_transactions_csv(request):
    """
    Exports the user's ledger as a downloadable CSV file.
    Respects currently active search and date filters.
    """
    qs = Transaction.objects.filter(user=request.user).select_related('category').order_by('-date')

    # Apply same filters if requested
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(description__icontains=q) | Q(category__name__icontains=q))

    type_filter = request.GET.get('type', '').strip().lower()
    if type_filter in ('income', 'expense'):
        qs = qs.filter(type=type_filter)

    category_id = request.GET.get('category', '').strip()
    if category_id:
        qs = qs.filter(category_id=category_id)

    start_date = request.GET.get('start_date', '').strip()
    if start_date:
        qs = qs.filter(date__gte=start_date)

    end_date = request.GET.get('end_date', '').strip()
    if end_date:
        qs = qs.filter(date__lte=end_date)

    filename = f"wealthtracker_ledger_{datetime.date.today().strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Type', 'Category', 'Description', 'Amount (INR)', 'Payment Method', 'Recurring'])

    for t in qs:
        writer.writerow([
            t.pk,
            t.date.strftime('%Y-%m-%d'),
            t.type.capitalize(),
            t.category.name if t.category else 'General',
            t.description,
            str(t.amount),
            t.payment_method or 'UPI',
            'Yes' if t.is_recurring else 'No',
        ])

    return response


@login_required
def import_transactions_csv(request):
    """
    Bank statement / ledger CSV importer.
    Parses CSV lines, normalizes dates and amounts, applies AI categorization,
    and batches transactions safely into the database.
    """
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['csv_file']
            try:
                # Read CSV content using TextIOWrapper with utf-8-sig (handles BOM)
                decoded_file = io.TextIOWrapper(uploaded_file.file, encoding='utf-8-sig')
                reader = csv.DictReader(decoded_file)

                # Normalize header field names to lowercase
                created_count = 0
                for row in reader:
                    norm = {k.strip().lower(): v.strip() for k, v in row.items() if k}

                    # 1. Parse Amount
                    raw_amount = (
                        norm.get('amount') or
                        norm.get('amount (inr)') or
                        norm.get('amt') or
                        norm.get('debit') or
                        norm.get('credit')
                    )
                    if not raw_amount:
                        continue

                    # Clean currency symbols and commas
                    clean_amt_str = raw_amount.replace('₹', '').replace(',', '').strip()
                    try:
                        amt_val = abs(Decimal(clean_amt_str))
                        if amt_val <= Decimal('0.00'):
                            continue
                    except Exception:
                        continue

                    # 2. Parse Date
                    raw_date = norm.get('date') or norm.get('transaction date') or norm.get('txn date')
                    parsed_date = datetime.date.today()
                    if raw_date:
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d'):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, fmt).date()
                                break
                            except ValueError:
                                pass

                    # 3. Parse Description
                    desc = (
                        norm.get('description') or
                        norm.get('memo') or
                        norm.get('narration') or
                        norm.get('merchant') or
                        norm.get('particulars') or
                        'Imported Transaction'
                    )

                    # 4. Parse or Infer Type
                    raw_type = norm.get('type', '').lower()
                    if raw_type in ('income', 'expense'):
                        txn_type = raw_type
                    elif norm.get('credit') and not norm.get('debit'):
                        txn_type = 'income'
                    else:
                        # Auto-infer from amount sign or common salary keywords
                        if 'salary' in desc.lower() or 'interest' in desc.lower() or 'dividend' in desc.lower():
                            txn_type = 'income'
                        else:
                            txn_type = 'expense'

                    # 5. Resolve or Predict Category
                    cat_name = norm.get('category', '').strip()
                    category_obj = None
                    if cat_name:
                        category_obj = Category.objects.filter(user=request.user, name__iexact=cat_name).first()

                    if not category_obj and desc:
                        _, _, matched_cat = predict_category(desc, user=request.user)
                        category_obj = matched_cat

                    # Create transaction record
                    Transaction.objects.create(
                        user=request.user,
                        amount=amt_val,
                        type=txn_type,
                        category=category_obj,
                        description=desc,
                        date=parsed_date,
                        payment_method='Other'
                    )
                    created_count += 1

                messages.success(request, f"🎉 Successfully imported {created_count} transactions from CSV!")
                return redirect('transaction_list')

            except Exception as e:
                messages.error(request, f"Failed to parse CSV file: {str(e)}")
    else:
        form = CSVImportForm()

    return render(request, 'tracker/import_transactions.html', {'form': form})


@login_required
def add_category_view(request):
    """
    Creates a new custom user classification label with icon and color.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f"Category '{category.name}' created successfully.")
            return redirect('add_category')
    else:
        form = CategoryForm()

    user_categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'tracker/add_category.html', {
        'form': form,
        'categories': user_categories
    })


@login_required
def delete_category_view(request, pk: int):
    """
    Deletes a custom category. If transactions are associated, safely dissociates them to General.
    """
    category = get_object_or_404(Category, pk=pk, user=request.user)
    cat_name = category.name
    category.delete()
    messages.success(request, f"Category '{cat_name}' removed. Any linked transactions remain safe under General.")
    return redirect('add_category')
