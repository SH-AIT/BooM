#!/bin/bash
5-deploy-embedding/deploy-embedding.sh
4-deploy-deepseek/deploy_deepseek.sh


POD_NAME=$(kubectl get pod -n euler-copilot | grep -E "^web-deploy" | awk '{print $1}')
# 替换HTML文件中的文字
kubectl exec -n euler-copilot "$POD_NAME" -- sed -i 's/openEuler Intelligence/万物昇长/g' /usr/share/nginx/html/index.html
kubectl exec -n euler-copilot "$POD_NAME" -- sed -i 's/openEuler Intelligence/万物昇长/g' /usr/share/nginx/html/404.html
kubectl exec -n euler-copilot "$POD_NAME" -- sed -i 's/openEuler Intelligence/万物昇长/g' /usr/share/nginx/html/error.html
kubectl exec -n euler-copilot "$POD_NAME" -- find /usr/share/nginx/html/ -name "*.js" -exec sed -i 's/openEuler Intelligence/万物昇长/g' {} \;





