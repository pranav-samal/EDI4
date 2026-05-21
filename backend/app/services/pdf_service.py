"""
PDF generation service for SHAP reports
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from app.models.application import Application
from app.models.credit_score import CreditScore


def generate_shap_pdf(application: Application, credit_score: CreditScore) -> bytes:
    """Generate PDF report for SHAP explanations"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    # Title
    elements.append(Paragraph("SHAP Explainability Report", title_style))
    elements.append(Paragraph(f"AI-Powered Credit Scoring Analysis", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Application Info
    info_data = [
        ['Application ID:', str(application.id)],
        ['Applicant:', application.user.full_name if application.user else 'N/A'],
        ['Application Type:', application.applicant_type.title()],
        ['Requested Amount:', f"₹{application.requested_amount:,.2f}"],
        ['Report Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Credit Score Summary
    elements.append(Paragraph("Credit Score Summary", heading_style))
    
    risk_color = colors.green if credit_score.risk_category == 'low' else \
                 colors.orange if credit_score.risk_category == 'medium' else colors.red
    
    summary_data = [
        ['Credit Score', 'Risk Category', 'Default Probability'],
        [
            str(round(credit_score.credit_score)),
            credit_score.risk_category.upper(),
            f"{credit_score.default_probability * 100:.1f}%"
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (1, 1), (1, 1), risk_color),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Understanding SHAP
    elements.append(Paragraph("Understanding SHAP Values", heading_style))
    shap_explanation = """
    SHAP (SHapley Additive exPlanations) values provide transparency into how the AI model 
    calculated your credit score. Each feature in your application contributes either positively 
    or negatively to your final score. Positive SHAP values (shown in green) increase your score, 
    while negative values (shown in red) decrease it. The magnitude indicates the strength of impact.
    """
    elements.append(Paragraph(shap_explanation, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Separate positive and negative features
    positive_features = [f for f in credit_score.shap_explanations if f['impact'] == 'positive']
    negative_features = [f for f in credit_score.shap_explanations if f['impact'] == 'negative']
    
    # Positive Factors
    if positive_features:
        elements.append(Paragraph("✓ Positive Factors (Improving Your Score)", heading_style))
        
        positive_data = [['Feature', 'Value', 'SHAP Impact']]
        for feature in positive_features:
            positive_data.append([
                format_feature_name(feature['feature_name']),
                f"{feature['feature_value']:.2f}",
                f"+{feature['shap_value']:.3f}"
            ])
        
        positive_table = Table(positive_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        positive_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0fdf4'), colors.white]),
        ]))
        elements.append(positive_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Negative Factors
    if negative_features:
        elements.append(Paragraph("✗ Negative Factors (Reducing Your Score)", heading_style))
        
        negative_data = [['Feature', 'Value', 'SHAP Impact']]
        for feature in negative_features:
            negative_data.append([
                format_feature_name(feature['feature_name']),
                f"{feature['feature_value']:.2f}",
                f"{feature['shap_value']:.3f}"
            ])
        
        negative_table = Table(negative_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        negative_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fef2f2'), colors.white]),
        ]))
        elements.append(negative_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    elements.append(Paragraph("Recommendations to Improve Your Score", heading_style))
    recommendations = []
    for feature in negative_features[:3]:
        rec = get_recommendation(feature['feature_name'])
        recommendations.append(f"• {rec}")
    
    if not recommendations:
        recommendations.append("• Continue maintaining your positive credit behavior")
        recommendations.append("• Keep making timely payments on all obligations")
        recommendations.append("• Monitor your credit regularly")
    
    for rec in recommendations:
        elements.append(Paragraph(rec, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Model Version: {credit_score.model_version}", footer_style))
    elements.append(Paragraph(f"© {datetime.now().year} Saral Credit - AI-Powered Credit Scoring Platform", footer_style))
    elements.append(Paragraph("This report is generated using machine learning and should be used for informational purposes.", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def format_feature_name(name: str) -> str:
    """Format feature names for display"""
    name_map = {
        'age': 'Age',
        'age_squared': 'Age Factor',
        'DebtRatio': 'Debt-to-Income Ratio',
        'debt_ratio_log': 'Debt Ratio (Adjusted)',
        'MonthlyIncome': 'Monthly Income',
        'monthly_income_log': 'Income Level',
        'NumberOfOpenCreditLinesAndLoans': 'Active Credit Lines',
        'NumberOfTimes90DaysLate': 'Serious Delinquencies (90+ days)',
        'NumberRealEstateLoansOrLines': 'Real Estate Loans',
        'NumberOfTime60-89DaysPastDueNotWorse': 'Late Payments (60-89 days)',
        'NumberOfDependents': 'Number of Dependents',
        'total_late_payments': 'Total Late Payments',
        'has_real_estate': 'Real Estate Ownership'
    }
    return name_map.get(name, name)


def get_recommendation(feature_name: str) -> str:
    """Get recommendation based on negative feature"""
    recommendations = {
        'NumberOfTimes90DaysLate': 'Avoid late payments by setting up automatic payments or reminders',
        'DebtRatio': 'Reduce your debt-to-income ratio by paying down existing debts',
        'total_late_payments': 'Maintain consistent on-time payments to build payment history',
        'NumberOfTime60-89DaysPastDueNotWorse': 'Focus on making all payments on time going forward',
        'NumberOfOpenCreditLinesAndLoans': 'Consider consolidating loans or closing unused credit lines',
        'MonthlyIncome': 'Increase income through additional work or side gigs',
        'NumberOfDependents': 'Manage household expenses efficiently',
        'has_real_estate': 'Building savings can help with future real estate investments'
    }
    return recommendations.get(feature_name, 'Continue building positive credit behavior')
