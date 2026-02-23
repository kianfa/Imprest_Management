class Navigator:
    def main_window_navigator(self, current_window):
        from app.ui.Dashboard_page import Dashboard
        dashboard = Dashboard()
        dashboard.show()
        current_window.close()
        return dashboard

    def dashboard_page_navigator_expense_entry(self, current_window):
        from app.ui.Receipt_Entry_Page import Expense_Receipt_Entry
        expense_entry_nav = Expense_Receipt_Entry()
        expense_entry_nav.show()
        current_window.close()
        return expense_entry_nav

    def dashboard_page_navigator_calling_page(self, current_window):
        from app.ui.Calling_Page import Calling_Page
        calling_nav = Calling_Page()
        calling_nav.show()
        current_window.close()
        return calling_nav

    def expense_entry_page_navigator(self, current_window):
        from app.ui.Dashboard_page import Dashboard
        dashboard_nav = Dashboard()
        dashboard_nav.show()
        current_window.close()
        return dashboard_nav

    def calling_entry_page_navigator(self, current_window):
        from app.ui.Dashboard_page import Dashboard
        dashboard_nav = Dashboard()
        dashboard_nav.show()
        current_window.close()
        return dashboard_nav