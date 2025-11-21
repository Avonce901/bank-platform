#!/usr/bin/env python
"""
Railway Deployment Status Checker
Uses Railway API to check build and deployment status
"""

import os
import sys
import json
import urllib.request
import urllib.error

def check_railway_status():
    """Check Railway deployment status via API"""
    
    token = os.getenv('RAILWAY_API_TOKEN')
    if not token:
        print("❌ RAILWAY_API_TOKEN not set")
        print("\nTo use this script:")
        print('  $env:RAILWAY_API_TOKEN="your-token-here"')
        print("  python check_deployment.py")
        return False
    
    project_id = "6ec8fec7-1efc-4fae-8505-536c903d9358"
    
    # GraphQL query to get deployment status
    query = """
    {
      project(id: "%s") {
        name
        environments {
          edges {
            node {
              name
              deployments(first: 1) {
                edges {
                  node {
                    id
                    status
                    createdAt
                    domains {
                      edges {
                        node {
                          domain
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """ % project_id
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = json.dumps({'query': query}).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            'https://api.railway.app/graphql',
            data=data,
            headers=headers
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'errors' in result:
                print("❌ API Error:")
                for error in result['errors']:
                    print(f"  {error.get('message', 'Unknown error')}")
                return False
            
            project = result.get('data', {}).get('project', {})
            if not project:
                print("❌ Project not found")
                return False
            
            print("=" * 70)
            print(f"PROJECT: {project.get('name', 'Unknown')}")
            print("=" * 70)
            
            environments = project.get('environments', {}).get('edges', [])
            
            for env in environments:
                env_node = env.get('node', {})
                env_name = env_node.get('name', 'Unknown')
                
                deployments = env_node.get('deployments', {}).get('edges', [])
                
                if deployments:
                    deployment = deployments[0].get('node', {})
                    status = deployment.get('status', 'Unknown')
                    
                    status_icon = {
                        'SUCCESS': '✅',
                        'FAILED': '❌',
                        'BUILDING': '⏳',
                        'CRASHED': '💥'
                    }.get(status, '❓')
                    
                    print(f"\nENVIRONMENT: {env_name}")
                    print(f"Status: {status_icon} {status}")
                    print(f"Created: {deployment.get('createdAt', 'Unknown')}")
                    
                    domains = deployment.get('domains', {}).get('edges', [])
                    if domains:
                        domain = domains[0].get('node', {}).get('domain', 'N/A')
                        print(f"Domain: https://{domain}")
                    
                    if status == 'SUCCESS':
                        print("\n✅ DEPLOYMENT SUCCESSFUL!")
                        print("\nNext steps:")
                        print("1. Add production variables in Railway dashboard:")
                        print("   - DEPLOYMENT_MODE = production")
                        print("   - STRIPE_API_KEY = sk_live_...")
                        print("   - STRIPE_WEBHOOK_SECRET = whsec_live_...")
                        print("\n2. Test the endpoint:")
                        if domains:
                            domain = domains[0].get('node', {}).get('domain', '')
                            print(f"   curl https://{domain}/health")
                        return True
                    elif status == 'FAILED':
                        print("\n❌ Deployment failed - check Railway logs")
                        return False
                    elif status == 'BUILDING':
                        print("\n⏳ Build in progress - check back in 3-5 minutes")
                        return False
            
            print("\n❓ No deployments found")
            return False
            
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = check_railway_status()
    sys.exit(0 if success else 1)
