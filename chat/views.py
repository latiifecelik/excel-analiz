import json
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import plotly.express as px
import plotly.utils
from django.views.decorators.csrf import ensure_csrf_cookie

def analyze_data(df):
    try:
        if df.empty:
            return {'error': 'Yüklenen Excel dosyası boş.'}
            
        graphs = []
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return {'error': 'Sayısal veri sütunu bulunamadı.'}
            
        # Calculate summary statistics
        summary_stats = df[numeric_cols].describe()
        summary_stats_dict = {}
        
        # Handle numeric columns
        for col in numeric_cols:
            summary_stats_dict[col] = {}
            # Basic statistics
            for stat, value in summary_stats[col].items():
                if pd.isna(value):
                    summary_stats_dict[col][stat] = None
                else:
                    summary_stats_dict[col][stat] = float(value)
            
            # Additional statistics
            summary_stats_dict[col]['skewness'] = float(df[col].skew())
            summary_stats_dict[col]['kurtosis'] = float(df[col].kurtosis())
            summary_stats_dict[col]['missing_values'] = int(df[col].isnull().sum())
            summary_stats_dict[col]['unique_values'] = int(df[col].nunique())

            # Create visualizations
            try:
                # Histogram with box plot
                fig_hist = px.histogram(df, x=col, title=f'{col} Dağılımı', marginal='box')
                fig_hist.update_layout(showlegend=True)
                graphs.append({
                    'title': f'{col} Dağılımı ve Kutu Grafiği',
                    'plots': [{
                        'data': json.loads(fig_hist.to_json())
                    }]
                })
                
                # Violin plot
                fig_violin = px.violin(df, y=col, box=True, title=f'{col} Violin Plot')
                graphs.append({
                    'title': f'{col} Violin Plot',
                    'plots': [{
                        'data': json.loads(fig_violin.to_json())
                    }]
                })
            except Exception as e:
                continue
        
        # Add correlation heatmap if multiple numeric columns exist
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, title='Korelasyon Matrisi')
            graphs.append({
                'title': 'Değişkenler Arası Korelasyon',
                'plots': [{
                    'data': json.loads(fig_corr.to_json())
                }]
            })
        
        return {
            'summary_stats': summary_stats_dict,
            'graphs': graphs
        }
        
    except Exception as e:
        return {'error': str(e)}

@ensure_csrf_cookie
def chat_view(request):
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file uploaded'}, status=400)

            file = request.FILES['file']
            if not file.name.endswith('.xlsx'):
                return JsonResponse({'error': 'Invalid file format. Please upload an Excel file.'}, status=400)

            # Read the Excel file
            df = pd.read_excel(file)
            
            # Perform analysis
            analysis_results = analyze_data(df)
            
            return JsonResponse(analysis_results)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'chat.html')

def analyze_view(request):
    if request.method == 'POST':
        if not request.FILES.get('file'):
            return JsonResponse({'error': 'Lütfen bir dosya yükleyin.'}, status=400)
        
        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            return JsonResponse({'error': 'Lütfen geçerli bir Excel (.xlsx) dosyası yükleyin.'}, status=400)
            
        try:
            df = pd.read_excel(file, engine='openpyxl')
            if df.empty:
                return JsonResponse({'error': 'Excel dosyası boş veya okunabilir veri içermiyor.'}, status=400)
                
            analysis = analyze_data(df)
            if 'error' in analysis:
                return JsonResponse({'error': analysis['error']}, status=400)
                
            return JsonResponse(analysis)
        except pd.errors.EmptyDataError:
            return JsonResponse({'error': 'Excel dosyası boş veya okunabilir veri içermiyor.'}, status=400)
        except pd.errors.ParserError:
            return JsonResponse({'error': 'Excel dosyası okunamadı. Lütfen dosyanın formatını kontrol edin.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Dosya işlenirken bir hata oluştu: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Geçersiz istek metodu. POST kullanın.'}, status=400)

def analyze_data(df):
    try:
        if df.empty:
            return {'error': 'Yüklenen Excel dosyası boş.'}
            
        graphs = []
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if len(numeric_cols) == 0:
            return {'error': 'Sayısal veri sütunu bulunamadı.'}
            
        # Enhanced summary statistics
        summary_stats = df[numeric_cols].describe()
        summary_stats_dict = {}
        
        # Handle numeric columns
        for col in numeric_cols:
            summary_stats_dict[col] = {}
            # Basic statistics
            for stat, value in summary_stats[col].items():
                if pd.isna(value):
                    summary_stats_dict[col][stat] = None
                else:
                    summary_stats_dict[col][stat] = float(value)
            
            # Additional statistics
            summary_stats_dict[col]['skewness'] = float(df[col].skew())
            summary_stats_dict[col]['kurtosis'] = float(df[col].kurtosis())
            summary_stats_dict[col]['missing_values'] = int(df[col].isnull().sum())
            summary_stats_dict[col]['unique_values'] = int(df[col].nunique())

        # Create enhanced visualizations
        for col in numeric_cols:
            try:
                # Create histogram with KDE
                fig_hist = px.histogram(df, x=col, title=f'{col} Dağılımı', marginal='box')
                fig_hist.update_layout(showlegend=True)
                graphs.append({
                    'title': f'{col} Dağılımı ve Kutu Grafiği',
                    'plots': [{
                        'data': json.loads(fig_hist.to_json())
                    }]
                })
                
                # Create violin plot
                fig_violin = px.violin(df, y=col, box=True, title=f'{col} Violin Plot')
                graphs.append({
                    'title': f'{col} Violin Plot',
                    'plots': [{
                        'data': json.loads(fig_violin.to_json())
                    }]
                })
                
                # Create time series if data has date/time
                if df.index.dtype.kind in 'M':
                    fig_time = px.line(df, y=col, title=f'{col} Zaman Serisi')
                    graphs.append({
                        'title': f'{col} Zaman Serisi Analizi',
                        'plots': [{
                            'data': json.loads(fig_time.to_json())
                        }]
                    })
                
                # Add correlation heatmap if multiple numeric columns exist
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    fig_corr = px.imshow(corr_matrix, title='Korelasyon Matrisi')
                    graphs.append({
                        'title': 'Değişkenler Arası Korelasyon',
                        'plots': [{
                            'data': json.loads(fig_corr.to_json())
                        }]
                    })
            except Exception as e:
                continue
        
        return {
            'summary_stats': summary_stats_dict,
            'graphs': graphs
        }
        
    except Exception as e:
        return {'error': str(e)}

def generate_ai_interpretation(df, summary_stats):
    interpretations = []
    
    for column in df.select_dtypes(include=['int64', 'float64']).columns:
        stats = summary_stats.loc[:, column]
        interpretation = {
            'column': column,
            'insights': [
                f"Ortalama {column} değeri: {stats['mean']:.2f}",
                f"En düşük {column} değeri: {stats['min']:.2f}",
                f"En yüksek {column} değeri: {stats['max']:.2f}",
                f"Standart sapma: {stats['std']:.2f}"
            ]
        }
        
        # Add distribution analysis
        if stats['std'] > stats['mean'] * 0.5:
            interpretation['insights'].append(f"{column} değerleri geniş bir aralığa yayılmış durumda.")
        else:
            interpretation['insights'].append(f"{column} değerleri ortalama etrafında yoğunlaşmış durumda.")
        
        # Add skewness analysis
        skewness = df[column].skew()
        if abs(skewness) > 1:
            if skewness > 0:
                interpretation['insights'].append(f"{column} dağılımı sağa çarpık (pozitif çarpıklık).")
            else:
                interpretation['insights'].append(f"{column} dağılımı sola çarpık (negatif çarpıklık).")
        
        interpretations.append(interpretation)
    
    return interpretations

def _validate_plot_data(plot_data):
    try:
        if not isinstance(plot_data, dict):
            raise ValueError('Invalid plot data format')

        required_keys = ['data', 'layout']
        for key in required_keys:
            if key not in plot_data:
                raise ValueError(f'Missing required key: {key}')

        if not isinstance(plot_data['data'], list):
            raise ValueError('Plot data must contain a list of traces')

    except Exception as e:
        raise ValueError(f'Plot validation error: {str(e)}')