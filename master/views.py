import openpyxl
from django.shortcuts import render
from .utils import util, istream, image, plot
import numpy as np
from matplotlib import pyplot as plt
from .utils.logger import Logger

# Create your views here.

INDEX_PAGE_URL = "master/index.html"


class DataStore(object):
    def __init__(self, df=None):
        self._df = df

    def update(self, df):
        self._df = df

    def get(self):
        return self._df

    def has_data(self):
        return self._df is not None


class ImageStore(object):
    def __init__(self, img=None):
        self._img = img

    def update(self, img):
        self._img = img

    def get(self):
        return self._img


class FrontEndDisplayPlacer(object):
    VIEW_TEMPLATE = {"excel_data": "", 'graph_div': "", "alert_message": "", 'new_visitor': "yes"}

    def __init__(self):
        self._view_dict = FrontEndDisplayPlacer.VIEW_TEMPLATE
        self._registered_ui = []

    def register(self, ui, data):
        """Register UIBase instance."""
        ui.create(view_cache=self, data=data)
        self._registered_ui.append(ui)

    def fresh(self, request):
        """Refresh all the registered UIs."""
        for ui in self._registered_ui:
            ui.fresh(view_cache=self, request=request)

    def alert(self, message):
        self._view_dict['alert_message'] = message

    def unalert(self):
        self._view_dict['alert_message'] = ""

    def loadForNewUser(self):
        self._view_dict['new_visitor'] = "yes"

    def loadForOldUser(self):
        self._view_dict['new_visitor'] = ""

    def update(self, key, value):
        self._view_dict[key] = value

    def get(self):
        return self._view_dict

    def hasKey(self, key):
        return key in self._view_dict

    def getValue(self, key):
        if key in self._view_dict:
            return self._view_dict[key]


class UIBase(object):
    def create(self, view_cache, data):
        """Create the UI with data.

        :param FrontEndDisplayPlacer view_cache: frontend view cache
        :param data: for each subclass of UIBase, it uses data to update the UI shown
        """
        pass

    def fresh(self, view_cache, request):
        """Create the UI with data.

        :param FrontEndDisplayPlacer view_cache: frontend view cache
        :param request: Django request, for each incoming request this would fresh and update the view
        """
        pass

    def getValue(self, request):
        pass


class DropDownList(UIBase):
    DEFAULT_VALUE = "--"

    def __init__(self, backend_data_name, dropdown_list_name):
        """UI for dropdown list.

        :param str backend_data_name: UI name for FrontEndDisplayPlacer, the backend gets the data and calculations and
            send to FrontEndDisplayPlacer for display.
        :param str dropdown_list_name: frontend uses this name to record feedback.
        """
        self._backend_data_name = backend_data_name
        self._dropdown_list_name = dropdown_list_name

    def create(self, view_cache, data):
        self._createDropdownListValues(view_cache=view_cache, dropdown_values=data)

    def fresh(self, view_cache, request):
        dropdown_values = self._getDropdownListValues(request)
        self._updateDropdownListView(view_cache=view_cache, current_dropdown_list_value=dropdown_values)

    def getValue(self, request):
        return self._getDropdownListValues(request)

    def _getDropdownListValues(self, request):
        return request.GET.get(self._dropdown_list_name)

    def _registerToViewCache(self, view_cache):
        if not view_cache or view_cache.hasKey(self._backend_data_name):
            return
        view_cache.update(key=self._backend_data_name,
                          value=[DropDownList.DEFAULT_VALUE])

    def _createDropdownListValues(self, view_cache, dropdown_values):
        if not view_cache:
            return
        if not view_cache.hasKey(self._backend_data_name):
            self._registerToViewCache(view_cache=view_cache)
        view_cache.update(self._backend_data_name, dropdown_values)

    def _updateDropdownListView(self, view_cache, current_dropdown_list_value=None):
        """Update dropdown list s.t. the shown value is the currently clicked one.

        Input: view_cache, type FrontEndDisplayPlacer
        Input: current_dropdown_list_value, type str, if None, use the default order. Otherwise, use its value as the
               first shown dropdown list value, while maintain the same order for the whole value list
        """
        if not view_cache or not view_cache.hasKey(self._backend_data_name):
            Logger.info("no key in view_cache, key = %s" % self._backend_data_name)
            return
        dropdown_values = view_cache.getValue(self._backend_data_name)
        if current_dropdown_list_value is not None:
            i = 0
            dropdown_index = -1
            while i < len(dropdown_values):
                if current_dropdown_list_value == dropdown_values[i]:
                    dropdown_index = i
                    break
                i += 1
            if dropdown_index < 0:
                return
            dropdown_values = list(dropdown_values[dropdown_index:]) + list(dropdown_values[:dropdown_index])
            view_cache.update(self._backend_data_name, dropdown_values)


dropdown_list1 = DropDownList(backend_data_name='data_columns_one',
                              dropdown_list_name='col_selected_one')
dropdown_list2 = DropDownList(backend_data_name='data_columns_two',
                              dropdown_list_name='col_selected_two')

data_store = DataStore()
img_store = ImageStore()
view_cache = FrontEndDisplayPlacer()

def index(request):
    """Return the index page view."""
    view_cache.unalert()
    if (data_store.get() is None):
        view_cache.loadForNewUser()
    else:
        view_cache.loadForOldUser()
    view_cache.fresh(request)

    if "GET" == request.method:

        if request.GET.get('column_button') == 'Click':
            col1 = dropdown_list1.getValue(request)
            col2 = dropdown_list2.getValue(request)
            df = data_store.get()

            if df is None:
                view_cache.alert("No data uploaded. Please re-upload if you have done that.")
            else:
                fig = plot.plotLine(df, col1, col2)
                img = image.drawMatplotLibGraph(fig)
                img_store.update(img)

                view_cache.update("graph_div", img_store.get())

        return render(request, INDEX_PAGE_URL, view_cache.get())
    else:
        file = request.FILES["excel_file"]
        df = istream.read_file(file)
        print(df)
        data_store.update(df)
        view_cache.update("excel_data", data_store.get().to_numpy())

        view_cache.register(ui=dropdown_list1, data=df.columns)
        view_cache.register(ui=dropdown_list2, data=df.columns)

        return render(request, 'master/index.html', view_cache.get())
