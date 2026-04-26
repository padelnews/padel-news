import re

with open('/Users/cristian/Sites/padel_news/scripts/dynamic_flow.py', 'r') as f:
    content = f.read()

# Find the update_actualidad_order function and add featured article update
old_func = '''def update_actualidad_order(state):
    """Update actualidad page - reorder news based on current tournament"""
    log("Updating actualidad page...")
    
    page_path = PAGES["actualidad"]
    with open(page_path, 'r') as f:
        content = f.read()
    
    phase = state.get("phase", "semifinal")
    
    # Update badge
    badge_text = f"🔴 {CURRENT_TOURNAMENT['name']} EN JUEGO"
    if phase == "FINISHED":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} TERMINADO"
    
    content = re.sub(
        r'<span class="live-badge">[^<]*</span>',
        f'<span class="live-badge">{badge_text}</span>',
        content
    )
    
    with open(page_path, 'w') as f:
        f.write(content)
    
    log("Actualidad page updated")'''

new_func = '''def update_actualidad_order(state):
    """Update actualidad page - reorder news based on current tournament"""
    log("Updating actualidad page...")
    
    page_path = PAGES["actualidad"]
    with open(page_path, 'r') as f:
        content = f.read()
    
    phase = state.get("phase", "semifinal")
    
    # Update badge
    badge_text = f"🔴 {CURRENT_TOURNAMENT['name']} EN JUEGO"
    if phase == "FINISHED":
        badge_text = f"🏆 {CURRENT_TOURNAMENT['name']} TERMINADO"
    
    content = re.sub(
        r'<span class="live-badge">[^<]*</span>',
        f'<span class="live-badge">{badge_text}</span>',
        content
    )
    
    # Update featured article based on phase
    if phase == "final":
        # Update featured article category for FINAL
        content = re.sub(
            r'<span class="news-card-category">[^<]*</span>',
            '<span class="news-card-category">🏆 FINAL MAÑANA</span>',
            content
        )
        
        # Update featured article description for FINAL
        old_desc = r'<p>\s*El torneo continúa[^<]*</p>'
        new_desc = '<p>¡La final está servida! Tapia/Coello vs Lebrón/Augsburger mañana domingo 26/04 a las 14:00. Los número uno buscarán su tercer título.</p>'
        content = re.sub(old_desc, new_desc, content)
    
    with open(page_path, 'w') as f:
        f.write(content)
    
    log("Actualidad page updated")'''

content = content.replace(old_func, new_func)

with open('/Users/cristian/Sites/padel_news/scripts/dynamic_flow.py', 'w') as f:
    f.write(content)

print("✅ Updated dynamic_flow.py to update featured article on phase change")
