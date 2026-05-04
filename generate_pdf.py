#!/usr/bin/env python3
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

# Create PDF
pdf_path = "SPRINT_BREAKDOWN.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                       rightMargin=0.75*inch, leftMargin=0.75*inch,
                       topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=6,
    alignment=0
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2e5c8a'),
    spaceAfter=8,
    spaceBefore=12,
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#555555'),
    spaceAfter=6,
    spaceBefore=8,
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=10,
    spaceAfter=4,
    leftIndent=20,
)

# Title
elements.append(Paragraph("GigBoard Project", title_style))
elements.append(Paragraph("Sprint Breakdown & User Stories", styles['Heading2']))
elements.append(Spacer(1, 0.1*inch))

# Sprints data
sprints = [
    {
        'number': 1,
        'title': 'Project Foundation & Authentication',
        'duration': 'April 6-7, 2026',
        'categories': {
            'Database & Setup': [
                'US 1.1: Set up Django project structure and configuration',
                'US 1.2: Initialize database models and migrations',
            ],
            'User Management': [
                'US 1.3: Implement user login and authentication',
                'US 1.4: Create user profile pages with editable information',
                'US 1.5: Add demo user accounts for testing',
            ],
            'Venue Management': [
                'US 1.6: Create Venue model with details and management',
                'US 1.7: Implement venue manager role and permissions',
                'US 1.8: Build venue switcher for multi-venue managers',
                'US 1.9: Create venue dashboard for managers',
            ],
            'Gig Listings': [
                'US 1.10: Create GigListing model with event details',
                'US 1.11: Build gig listing creation form',
                'US 1.12: Implement gig listing display and filtering',
                'US 1.13: Add gig closure functionality',
                'US 1.14: Create gig routing and templates',
                'US 1.15: Add basic CSS styling',
            ]
        }
    },
    {
        'number': 2,
        'title': 'Lessons & Networking',
        'duration': 'April 12, 2026',
        'categories': {
            'Lesson Booking System': [
                'US 2.1: Create lesson model and booking system',
                'US 2.2: Build lesson slot management',
                'US 2.3: Implement lesson listing and discovery',
            ],
            'Performer Networking': [
                'US 2.4: Build collaboration request system',
                'US 2.5: Implement networking features with test coverage',
                'US 2.6: Fix base template for unified UI',
            ]
        }
    },
    {
        'number': 3,
        'title': 'Infrastructure & Testing',
        'duration': 'April 13-14, 2026',
        'categories': {
            'Production Readiness': [
                'US 3.1: Configure production database connection (Neon)',
                'US 3.2: Set up Merge Pull Request #3 for gig listings',
            ],
            'Quality Assurance': [
                'US 3.3: Write and implement test suite for lesson features',
            ]
        }
    },
    {
        'number': 4,
        'title': 'Discovery & User Experience',
        'duration': 'April 19-20, 2026',
        'categories': {
            'Collaboration Workflow': [
                'US 4.1: Implement accept/decline actions for collaboration requests',
                'US 4.2: Build collaboration request management flow',
            ],
            'Calendar & Time Management': [
                'US 4.3: Add event calendar for performers and venues',
            ],
            'Profile Enhancements': [
                'US 4.4: Add social media links to performer profiles',
                'US 4.5: Add music preferences and interests fields',
                'US 4.6: Display upcoming gigs on performer profiles',
                'US 4.7: Display past performances on performer profiles',
                'US 4.8: Resolve merge conflicts for profile URLs',
            ],
            'Discovery Features': [
                'US 4.9: Build performer browsing and search',
                'US 4.10: Build venue browsing and search',
            ],
            'UI/UX Improvements': [
                'US 4.11: Consolidate and redesign navigation bar',
                'US 4.12: Integrate bootstrap icons for enhanced UI',
            ]
        }
    },
    {
        'number': 5,
        'title': 'Reviews, Verification & Notifications',
        'duration': 'April 23-25, 2026',
        'categories': {
            'Quality & Feedback': [
                'US 5.1: Create Review model and review functionality',
                'US 5.2: Implement review eligibility restrictions',
                'US 5.3: Display review cards on performer/venue profiles',
                'US 5.4: Build gig completion verification workflow',
            ],
            'User Engagement': [
                'US 5.5: Implement in-app notification system',
                'US 5.6: Notify performers of review/feedback activity',
            ],
            'Bug Fixes': [
                'US 5.7: Fix template syntax error on venue profiles',
            ]
        }
    },
    {
        'number': 6,
        'title': 'User Registration & Account Creation',
        'duration': 'May 1, 2026',
        'categories': {
            'Account Management': [
                'US 6.1: Implement user registration/sign-up flow',
                'US 6.2: Add role selection during account creation',
                'US 6.3: Create account migrations for new user fields',
            ]
        }
    },
    {
        'number': 7,
        'title': 'Social Features',
        'duration': 'May 3, 2026',
        'categories': {
            'Fan Engagement': [
                'US 7.1: Implement fan following functionality',
                'US 7.2: Display performer schedule visibility for fans',
                'US 7.3: Build notifications for followers on schedule updates',
            ]
        }
    }
]

# Build document
for sprint in sprints:
    # Sprint heading
    sprint_heading = f"Sprint {sprint['number']}: {sprint['title']}"
    elements.append(Paragraph(sprint_heading, heading_style))
    elements.append(Paragraph(f"<b>Duration:</b> {sprint['duration']}", body_style))
    elements.append(Spacer(1, 0.08*inch))
    
    # Categories and user stories
    for category, stories in sprint['categories'].items():
        elements.append(Paragraph(category, subheading_style))
        for story in stories:
            elements.append(Paragraph(story, body_style))
        elements.append(Spacer(1, 0.05*inch))
    
    elements.append(Spacer(1, 0.1*inch))

# Summary
elements.append(PageBreak())
elements.append(Paragraph("Project Summary", heading_style))
elements.append(Spacer(1, 0.1*inch))

summary_data = [
    ['Metric', 'Value'],
    ['Total Sprints', '7'],
    ['Project Duration', 'April 6 - May 3, 2026 (~4 weeks)'],
    ['Total User Stories', '45+'],
]

summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))

elements.append(summary_table)
elements.append(Spacer(1, 0.2*inch))

# Key features
features_text = """
<b>Key Features Delivered:</b><br/>
• Complete user authentication and profile management<br/>
• Gig listing and booking system<br/>
• Lesson scheduling platform<br/>
• Performer/venue discovery<br/>
• Review and rating system<br/>
• In-app notifications<br/>
• Social following features<br/>
• Multi-venue management capabilities<br/>
"""
elements.append(Paragraph(features_text, body_style))

# Build PDF
doc.build(elements)
print(f"PDF created successfully: {pdf_path}")
