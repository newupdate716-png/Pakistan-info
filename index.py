from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Vercel-এর জন্য WSGI handler এক্সপোজ করা
app.debug = False

@app.route('/info', methods=['GET'])
def info():
    """
    Get SIM/CNIC information
    Usage: /info?num=03359736848
    """
    num = request.args.get('num', '').strip()
    
    if not num:
        return jsonify({
            'success': False,
            'error': 'Number is required. Use: /info?num=03359736848'
        }), 400
    
    num = num.replace('-', '').replace(' ', '')
    
    if not num.isdigit():
        return jsonify({
            'success': False,
            'error': 'Number must contain only digits'
        }), 400
    
    if len(num) not in [10, 11, 13]:
        return jsonify({
            'success': False,
            'error': 'Invalid length. Mobile: 10-11 digits, CNIC: 13 digits'
        }), 400
    
    if len(num) == 10 and num.startswith('3'):
        num = '0' + num
    
    num_type = 'sim' if len(num) in [10, 11] else 'cnic'
    
    form_data = {
        'post_id': '413',
        'form_id': '5e17544',
        'referer_title': 'Search SIM and CNIC Details - Instant Ownership Check',
        'queried_id': '413',
        'form_fields[search]': num,
        'action': 'elementor_pro_forms_send_form',
        'referrer': 'https://simownership.com/search/'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(
            'https://simownership.com/wp-admin/admin-ajax.php',
            headers=headers,
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if (data.get('success') and 
                'data' in data and 
                'data' in data['data'] and 
                'results' in data['data']['data']):
                
                results = data['data']['data']['results']
                return jsonify({
                    'success': True,
                    'number': num,
                    'type': num_type,
                    'results': results,
                    'count': len(results)
                })
            else:
                return jsonify({
                    'success': False,
                    'number': num,
                    'type': num_type,
                    'error': 'No records found',
                    'results': []
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': f'Service error: {response.status_code}'
            }), 503
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timeout'}), 504
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Pakistan Number Info API',
        'usage': '/info?num=03359736848',
        'examples': {
            'mobile': '/info?num=03359736848',
            'mobile_no_zero': '/info?num=3359736848',
            'cnic': '/info?num=1234567890123'
        }
    })