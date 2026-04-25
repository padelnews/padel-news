#!/bin/bash
# Padel News - Server Startup Script

echo "🎾 Padel News Server"
echo "===================="

# Check if Apache is configured for port 8080
if grep -q "Listen 8080" /etc/apache2/httpd.conf 2>/dev/null || [ -f /etc/apache2/other/padel_news.conf ]; then
    echo "✓ Apache configuration found"
    echo ""
    echo "To start Apache with the padel news site:"
    echo "  1. Copy apache_config.conf to /etc/apache2/other/padel_news.conf"
    echo "  2. sudo apachectl restart"
    echo "  3. Visit http://localhost:8080"
else
    echo "⚠ Apache config not found in system directories"
    echo ""
    echo "Manual setup required:"
    echo "  sudo cp apache_config.conf /etc/apache2/other/padel_news.conf"
    echo "  sudo apachectl restart"
fi

echo ""
echo "Alternative: Use Python HTTP server for testing:"
echo "  cd /Users/cristian/Sites/padel_news"
echo "  python3 -m http.server 8080"
echo ""
echo "Then visit: http://localhost:8080"
