#!/bin/bash
# Script to deploy Lambda function for AutoVault
# Usage: ./deploy_lambda.sh

set -e

echo "=========================================="
echo "AutoVault Lambda Deployment"
echo "=========================================="

# Create deployment package directory
PACKAGE_DIR="lambda_package"
ZIP_FILE="lambda_function.zip"

echo ""
echo "📦 Creating deployment package..."

# Clean up old package
rm -rf $PACKAGE_DIR
rm -f $ZIP_FILE

# Create package directory
mkdir -p $PACKAGE_DIR

# Copy Lambda function
cp lambda_function.py $PACKAGE_DIR/

# Install dependencies
echo "📥 Installing dependencies..."
pip3 install -r lambda_requirements.txt -t $PACKAGE_DIR/ --quiet

# Create zip file
echo "📦 Creating zip file..."
cd $PACKAGE_DIR
zip -r ../$ZIP_FILE . -q
cd ..

# Clean up
rm -rf $PACKAGE_DIR

echo ""
echo "✅ Deployment package created: $ZIP_FILE"
echo ""
echo "📝 Next steps:"
echo "   1. Go to AWS Lambda Console"
echo "   2. Create/update function: autovault-expiry-processor"
echo "   3. Upload $ZIP_FILE"
echo "   4. Configure environment variables"
echo "   5. Set up EventBridge rule (see LAMBDA_SETUP_GUIDE.md)"
echo ""
echo "📖 See LAMBDA_SETUP_GUIDE.md for detailed instructions"

