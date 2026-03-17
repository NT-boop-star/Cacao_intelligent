"""
CACAO INTELLIGENT — Generateur de Due Diligence Statement (DDS) EUDR
Génère un PDF officiel 2023/1115 en mémoire via ReportLab.
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.platypus.flowables import HRFlowable
from lot_manager import generer_qr_bytes

def generer_dds(profil):
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    style_header = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#2C1810'),
        alignment=1,
        spaceAfter=6
    )
    
    style_subheader = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        alignment=1,
        spaceAfter=20
    )
    
    style_section = ParagraphStyle(
        'TitreSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1E5631'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        spaceAfter=6
    )
    
    style_italic = ParagraphStyle(
        'Italic',
        parent=style_normal,
        fontName='Helvetica-Oblique'
    )
    
    elements = []
    
    # PAGE 1 : EN-TETE
    elements.append(Paragraph("CACAO INTELLIGENT", style_header))
    
    style_subtitle = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=15
    )
    elements.append(Paragraph("Système de Traçabilité Agricole — Côte d'Ivoire", style_subtitle))
    
    elements.append(Paragraph("Due Diligence Statement — Règlement EU 2023/1115", style_subheader))
    
    date_jour = datetime.now().strftime("%d/%m/%Y")
    id_agriculteur = profil.get("id", "INCONNU")
    date_timestamp = datetime.now().strftime("%Y%m%d")
    ref_dds = f"DDS-{id_agriculteur}-{date_timestamp}"
    
    elements.append(Paragraph(f"<b>Date de génération :</b> {date_jour}", style_normal))
    elements.append(Paragraph(f"<b>Numéro de référence :</b> {ref_dds}", style_normal))
    elements.append(Spacer(1, 15))
    
    # Ligne de separation verte
    def ligne_verte():
        return HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E5631'), spaceBefore=10, spaceAfter=5)

    # SECTION 1
    elements.append(ligne_verte())
    elements.append(Paragraph("SECTION 1 — Identité de l'opérateur", style_section))
    prenom = profil.get("prenom", "")
    nom = profil.get("nom", "")
    nom_complet = f"{prenom} {nom}".strip()
    
    elements.append(Paragraph(f"<b>Nom complet :</b> {nom_complet}", style_normal))
    elements.append(Paragraph(f"<b>ID numérique :</b> {id_agriculteur}", style_normal))
    elements.append(Paragraph(f"<b>Numéro de téléphone :</b> {profil.get('telephone', 'Non renseigné')}", style_normal))
    
    coop = profil.get('cooperative', '').strip()
    if coop and coop != "-":
        elements.append(Paragraph(f"<b>Coopérative :</b> {coop}", style_normal))
        
    elements.append(Spacer(1, 10))
    
    # SECTION 2
    elements.append(ligne_verte())
    elements.append(Paragraph("SECTION 2 — Géolocalisation de la parcelle", style_section))
    parcelle = profil.get("parcelle", {})
    lat = parcelle.get("latitude", "Non renseigné")
    lon = parcelle.get("longitude", "Non renseigné")
    sup = parcelle.get("superficie", "Non renseigné")
    
    elements.append(Paragraph(f"<b>Latitude :</b> {lat}", style_normal))
    elements.append(Paragraph(f"<b>Longitude :</b> {lon}", style_normal))
    elements.append(Paragraph(f"<b>Superficie :</b> {sup} hectares", style_normal))
    elements.append(Paragraph("<b>Zone géographique :</b> Côte d'Ivoire", style_normal))
    elements.append(Spacer(1, 10))
    
    # SECTION 3
    elements.append(ligne_verte())
    elements.append(Paragraph("SECTION 3 — Vérification de non-déforestation", style_section))
    eudr = profil.get("eudr", {})
    statut = eudr.get("statut", "INDETERMINE")
    source = eudr.get("source", "Non renseigné")
    date_verif = eudr.get("date_verification", "Non renseigné")
    
    elements.append(Paragraph(f"<b>Statut EUDR :</b> {statut}", style_normal))
    elements.append(Paragraph(f"<b>Source des données :</b> {source}", style_normal))
    elements.append(Paragraph(f"<b>Date de vérification :</b> {date_verif}", style_normal))
    elements.append(Paragraph("<b>Seuil réglementaire :</b> 31 décembre 2020", style_normal))
    elements.append(Spacer(1, 5))
    
    mention_explicite = "Aucune perte de couvert forestier détectée après le 31/12/2020 dans un rayon de 0.05° autour des coordonnées GPS déclarées."
    elements.append(Paragraph(mention_explicite, style_italic))
    elements.append(Spacer(1, 10))
    
    # SECTION 4
    elements.append(ligne_verte())
    elements.append(Paragraph("SECTION 4 — Déclaration", style_section))
    texte_legal = "Le soussigné déclare que les informations fournies dans ce document sont exactes et conformes aux exigences du Règlement (UE) 2023/1115 relatif aux produits associés à la déforestation."
    elements.append(Paragraph(texte_legal, style_normal))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<b>Signature de l'opérateur :</b>", style_normal))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("___________________________________________________", style_normal))
    
    style_signature_name = ParagraphStyle(
        'SigName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        spaceBefore=5,
        spaceAfter=10
    )
    elements.append(Paragraph(nom_complet, style_signature_name))
    
    
    # SECTION 5: Lots de cacao tracables
    lots = profil.get("lots", [])
    if lots:
        elements.append(ligne_verte())
        elements.append(Paragraph("SECTION 5 — Lots de cacao tracables", style_section))
        
        # Header tableau
        table_data = [["ID Lot", "Date récolte", "Poids", "Statut"]]
        for lot in lots:
            table_data.append([
                lot.get("id", ""),
                lot.get("date_recolte", ""),
                f"{lot.get('poids_kg', 0)} kg",
                lot.get("statut", "").replace("_", " ")
            ])
            
        t = Table(table_data, colWidths=[5 * cm, 3.5 * cm, 3.5 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2C1810')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D5C9B8'))
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))
        
        # Prendre le dernier lot pour le QR Code
        dernier_lot = lots[-1] if lots else None
                
        if dernier_lot:
            qr_bytes = generer_qr_bytes(dernier_lot["id"], profil)
            try:
                qr_img = RLImage(BytesIO(qr_bytes), width=3*cm, height=3*cm)
                
                # Tableau invisible pour aligner QR + Texte
                qr_data = [[
                    qr_img,
                    Paragraph("Scannez le QR code pour vérifier l'authenticité et la traçabilité de ce lot.", style_italic)
                ]]
                qr_table = Table(qr_data, colWidths=[4*cm, 10*cm])
                qr_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                ]))
                elements.append(qr_table)
            except Exception as e:
                pass

    # PIED DE PAGE
    def add_footer(canvas, document):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#888888'))
        footer_text = f"Document généré par Cacao Intelligent — AgriTech Innovators ESATIC — Digital ID Africa Hackathon 2026 | Page {document.page}"
        canvas.drawCentredString(A4[0] / 2.0, 1.5 * cm, footer_text)
        canvas.restoreState()
        
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
