from google.cloud import billing
from google.cloud import billing_budgets_v1
from google.cloud.billing_budgets_v1 import BudgetService
from google.cloud.billing_budgets_v1.types import Budget
from google.cloud.billing_budgets_v1.types import BudgetAmount
from google.cloud.billing_budgets_v1.types import ThresholdRule
from google.cloud.billing_budgets_v1.types import AllUpdatesRule
from google.protobuf import field_mask_pb2
import os

class BudgetMonitor:
    def __init__(self, project_id, billing_account_id):
        self.project_id = project_id
        self.billing_account_id = billing_account_id
        self.client = billing_budgets_v1.BudgetServiceClient()
        
    def create_budget(self, amount_usd=10.0, threshold_percentages=[0.5, 0.8, 1.0]):
        """Belirli bir miktar için bütçe ve alarm oluşturur"""
        try:
            parent = f"billingAccounts/{self.billing_account_id}"
            
            # Bütçe miktarını ayarla
            budget_amount = BudgetAmount()
            budget_amount.specified_amount.currency_code = "USD"
            budget_amount.specified_amount.units = str(int(amount_usd))
            budget_amount.specified_amount.nanos = int((amount_usd % 1) * 1e9)
            
            # Eşik kurallarını oluştur
            threshold_rules = [
                ThresholdRule(threshold_percent=percentage)
                for percentage in threshold_percentages
            ]
            
            # E-posta bildirimlerini ayarla
            all_updates_rule = AllUpdatesRule(
                monitoring_notification_channels=[
                    f"projects/{self.project_id}/notificationChannels/email"
                ],
                schema_version="1.0"
            )
            
            # Bütçeyi oluştur
            budget = Budget(
                display_name=f"Vertex AI Budget ${amount_usd}",
                budget_filter={
                    "projects": [f"projects/{self.project_id}"],
                    "services": ["services/aiplatform.googleapis.com"]
                },
                amount=budget_amount,
                threshold_rules=threshold_rules,
                all_updates_rule=all_updates_rule
            )
            
            response = self.client.create_budget(
                parent=parent,
                budget=budget
            )
            
            print(f"Bütçe başarıyla oluşturuldu: {response.name}")
            return response
            
        except Exception as e:
            print(f"Bütçe oluşturma hatası: {str(e)}")
            return None
    
    def get_current_usage(self):
        """Mevcut kullanımı kontrol et"""
        try:
            billing_client = billing.CloudBillingClient()
            
            # Projenin fatura bilgilerini al
            project_name = f"projects/{self.project_id}"
            billing_info = billing_client.get_project_billing_info(name=project_name)
            
            if not billing_info.billing_enabled:
                return "Faturalama bu proje için etkin değil"
            
            # Mevcut kullanımı al
            billing_account = f"billingAccounts/{self.billing_account_id}"
            current_usage = billing_client.get_billing_account(name=billing_account)
            
            return {
                "project_id": self.project_id,
                "billing_account": self.billing_account_id,
                "current_usage": current_usage
            }
            
        except Exception as e:
            print(f"Kullanım kontrolü hatası: {str(e)}")
            return None
    
    def check_budget_alerts(self):
        """Bütçe uyarılarını kontrol et"""
        try:
            parent = f"billingAccounts/{self.billing_account_id}"
            
            # Tüm bütçeleri listele
            budgets = self.client.list_budgets(parent=parent)
            
            alerts = []
            for budget in budgets:
                # Her bütçe için mevcut durumu kontrol et
                current_amount = float(budget.amount.specified_amount.units)
                for rule in budget.threshold_rules:
                    threshold = current_amount * rule.threshold_percent
                    alerts.append({
                        "budget_name": budget.display_name,
                        "threshold_percent": rule.threshold_percent * 100,
                        "threshold_amount": threshold,
                        "current_amount": current_amount
                    })
            
            return alerts
            
        except Exception as e:
            print(f"Bütçe kontrol hatası: {str(e)}")
            return None

# Kullanım örneği
if __name__ == "__main__":
    # Google Cloud kimlik bilgilerini ayarla
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"
    
    # Monitor'ü başlat
    monitor = BudgetMonitor(
        project_id="your-project-id",
        billing_account_id="your-billing-account-id"
    )
    
    # $10'lık bütçe oluştur
    monitor.create_budget(amount_usd=10.0, threshold_percentages=[0.5, 0.8, 1.0])
    
    # Mevcut kullanımı kontrol et
    usage = monitor.get_current_usage()
    print("Mevcut kullanım:", usage)
    
    # Bütçe uyarılarını kontrol et
    alerts = monitor.check_budget_alerts()
    print("Bütçe uyarıları:", alerts) 