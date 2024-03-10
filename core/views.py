from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic import ListView

from .models import Dispatch


@require_POST
@staff_member_required
def dispatch_action_view(request, pk):
    dispatch = get_object_or_404(Dispatch, pk=pk)
    if 'send_now' in request.POST:
        dispatch.send()
    elif 'toggle_activation' in request.POST:
        dispatch.toggle_activation()
    return redirect('dispatch-detail', pk=dispatch.pk)


def real_time_stats(request, dispatch_id):
    dispatch = Dispatch.objects.get(pk=dispatch_id)
    data = {
        'recipients_count': dispatch.get_recipient_count(),
        'sent_times': dispatch.sent_times,
    }
    return JsonResponse(data)


class DispatchListView(ListView):
    model = Dispatch
    template_name = 'core/dispatch_list.html'
    context_object_name = 'dispatches'


class DispatchDetailView(DetailView):
    model = Dispatch
    template_name = 'core/dispatch_detail.html'
    context_object_name = 'dispatch'
