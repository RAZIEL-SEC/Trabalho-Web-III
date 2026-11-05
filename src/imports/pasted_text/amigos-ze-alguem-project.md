# Amigos do Zé Alguém — Responsive Institutional Website and Donation Management Dashboard

## Project Overview

Design and prototype a responsive web application for **Amigos do Zé Alguém**, a Brazilian nonprofit organization focused on fighting hunger and social vulnerability.

The product has two connected experiences:

1. A public-facing institutional website for supporters, donors, volunteers, and people who want to learn about the organization.
2. A private administrative dashboard for the organization’s responsible coordinator to manage donation movements and consult their history.

The interface must be in **Brazilian Portuguese (pt-BR)**. Use realistic Portuguese content, Brazilian date formats (DD/MM/YYYY), and Brazilian terminology.

This is an academic web development project. Keep the scope realistic and avoid introducing complex features that have not been defined.

## Organization and Brand Identity

The organization’s logo is a **blue cap with a curved brim**, featuring the words “Amigos do Zé Alguém”. A heart replaces the letter “o” in “Amigos”.

Use this as the central brand reference. If the exact logo asset is unavailable, create a simple placeholder representation inspired by the blue cap and heart detail. Do not invent a completely different logo.

### Brand personality

* Institutional
* Welcoming
* Human
* Socially conscious
* Trustworthy
* Accessible
* Community-oriented

### Main colors

Use **blue and white** as the primary brand colors.

Suggested visual direction:

* Deep blue for navigation, headings, buttons, and important actions.
* White for the main background and clean content surfaces.
* Soft blue shades for cards, highlights, and secondary backgrounds.
* Neutral gray for supporting text, dividers, and form borders.

Use color contrast that supports accessibility. Avoid an overly corporate, financial, or e-commerce appearance.

## Organization’s Social Values

The organization has a social mandala representing these nine values:

1. Humanização
2. Geração de Renda
3. Cidadania
4. Vínculo Familiar
5. Direito à Moradia Digna
6. Acesso à Saúde
7. Segurança Alimentar
8. Conscientização
9. Direito à Educação

Create a visually meaningful section for these values on the institutional website. Consider a circular mandala-inspired composition on desktop and an accessible grid or stacked layout on mobile.

Keep all nine values readable. Do not omit or rename any value.

## Target Users

### Public website visitors

Supporters and potential donors will access the website primarily through mobile phones.

They need to:

* Understand what the organization does.
* Learn about its social impact and activities.
* Discover ways to help.
* Find volunteer registration information.
* Access the organization’s contact and social media channels.

### Administrative user

The coordinator will primarily use the administrative dashboard on a desktop computer.

She needs to:

* Register incoming donations.
* Register outgoing donations or use of supplies.
* Record dates, quantities, and relevant details.
* Identify who recorded each movement.
* Consult previous records and their history.
* Navigate the system easily without unnecessary complexity.

## Public Website — Required Pages and Sections

Create a complete, navigable public website with the following sections.

### 1. Home

Create a welcoming homepage with:

* A clear header featuring the logo.
* Navigation links.
* A prominent introductory hero section.
* A concise description of the organization’s mission.
* A primary call to action: “Como ajudar”.
* A secondary call to action: “Conheça nossas ações”.
* A section highlighting the organization’s activities.
* A preview of its social values.
* A closing call to action encouraging community support.
* A footer with contact and social media placeholders.

Use authentic, human-centered imagery related to food distribution, community support, volunteers, and education. Avoid exploitative or stereotypical depictions of people experiencing vulnerability.

### 2. Quem Somos

Include:

* The organization’s history and mission.
* Its work fighting hunger and social vulnerability.
* Its community-oriented approach.
* The nine values of its social mandala.

Use clear headings and short, readable paragraphs.

### 3. Nossas Ações

Present the organization’s activities in a visual card layout.

Include examples such as:

* Distribution of prepared meals (quentinhas).
* Basic food baskets.
* Hygiene kits.
* Clothing campaigns.
* “Amigos da Escola”, a literacy and educational support activity for children.

Make it easy to understand what each activity is and whom it supports.

Do not invent exact current quantities, schedules, or impact statistics unless explicitly presented as illustrative content.

### 4. Como Ajudar

Create a clear page explaining ways to support the organization.

Include:

* Donation guidance.
* A section for people interested in volunteering.
* A prominent “Quero ser voluntário” button.
* A placeholder link for the existing volunteer registration form, such as Google Forms.
* Contact information placeholders for questions about donations.

Do not create payment processing, checkout, recurring financial donations, or financial account forms.

### 5. Contato

Include:

* Contact information placeholders.
* Social media links as placeholders.
* A clear way to contact the organization.

Do not invent real addresses, phone numbers, email addresses, or social media handles.

## Administrative Dashboard — Required Experience

Create a separate, private administrative area with a distinct but consistent visual identity.

The dashboard should be optimized for desktop while remaining usable on mobile.

### 1. Login

Create a simple login screen with:

* Email field.
* Password field.
* “Entrar” button.
* Organization logo.
* Clear validation and error states.

This is a visual prototype. Do not implement real authentication or claim that the system is secure or connected to a real account.

### 2. Dashboard Overview

After entering the prototype, display an administrative dashboard with:

* A welcome message.
* A clear navigation sidebar on desktop.
* A compact navigation pattern on mobile.
* A summary of recent donation movements.
* Simple summary cards for incoming and outgoing movements.
* A prominent “Registrar movimentação” action.
* A recent activity table or list.

Use sample data clearly intended for demonstration.

Avoid introducing advanced inventory analytics, financial reports, forecasting, or stock alerts.

### 3. Donation Movements

This is the central feature of the administrative system.

Create a unified movements page with:

* A table of recorded movements on desktop.
* A responsive card or list layout on mobile.
* A clear movement type: “Entrada” or “Saída”.
* Date of movement.
* Item or donation description.
* Quantity.
* Unit of measurement, when applicable (kg, unidades, litros, etc.).
* Person responsible for recording the movement.
* Optional notes.

Include simple filters for:

* Movement type.
* Date or date range.
* Item or description.

Include a search field to find records.

Make the movement history easy to scan and understand.

### 4. Register a Movement

Create a form for recording a new donation movement.

Fields:

* Tipo de movimentação: Entrada / Saída.
* Data da movimentação.
* Item ou descrição.
* Quantidade.
* Unidade de medida.
* Observações (optional).

Display the logged-in administrative user as the person recording the movement. In this prototype, use a clearly fictional sample user.

The form should provide:

* Required-field validation.
* Clear labels and helpful hints.
* A primary “Salvar movimentação” button.
* A secondary “Cancelar” action.
* A success confirmation after saving sample data.

The form should adapt based on whether the movement is an entry or an exit, but do not invent complex business rules.

### 5. Movement Details and Audit History

Auditability is an important requirement.

Each movement should display:

* Movement type.
* Date.
* Item description.
* Quantity and unit.
* Who recorded it.
* When the record was created.
* Relevant notes.

Create a detail view or side panel that allows the administrator to inspect a movement.

Include a simple activity history demonstrating that records can be traced to the user who created them.

Do not claim to implement immutable audit logs, tamper-proof records, or enterprise-grade security. This is a prototype exploring the user experience and data requirements.

If editing is demonstrated, clearly show that a record was updated and include a sample “Última atualização” field. Do not silently overwrite history.

### 6. Empty, Loading, and Error States

Design appropriate states for:

* No movements registered yet.
* No search results.
* Missing required form fields.
* Successful movement registration.
* A generic loading state.

Keep error messages understandable and in Brazilian Portuguese.

## Interaction and Prototype Requirements

Build a functional-feeling interactive prototype rather than a collection of disconnected static screens.

Implement sample interactions where possible:

* Navigate between public website sections.
* Open the administrative login.
* Enter the dashboard using a prototype-only interaction.
* Navigate between dashboard and movements.
* Open the movement registration form.
* Switch between Entrada and Saída.
* Validate required fields.
* Save a sample movement and display it in the movements list.
* Open a movement’s details.
* Search and filter sample movements.
* Navigate back and cancel forms.

Use local prototype state or mock data where supported.

Do not connect to real databases, payment providers, Google accounts, or external services. Do not imply that data is actually being stored on a server.

## Responsive Design

Design for two primary usage contexts.

### Mobile-first public experience

* Prioritize mobile usability.
* Use a compact navigation menu.
* Large, accessible touch targets.
* Readable text and clear calls to action.
* Stack content vertically.
* Avoid overly dense layouts.
* Make the volunteer and donation pathways easy to find.

### Desktop-first administrative experience

* Use a clear sidebar or structured navigation.
* Make effective use of screen width.
* Keep tables readable.
* Use comfortable spacing and clear hierarchy.
* Keep common actions visible and easy to access.

Ensure the layout adapts gracefully between mobile, tablet, and desktop.

## Visual Design System

Create a consistent reusable design system with:

* Primary and secondary buttons.
* Form fields and labels.
* Navigation components.
* Cards.
* Tables and responsive record lists.
* Status badges for Entrada and Saída.
* Modals or detail panels.
* Feedback messages.
* Consistent spacing, typography, and border radii.

Use a clean, welcoming, modern design. Avoid excessive gradients, excessive animations, clutter, and overly decorative dashboard components.

## Content and Scope Constraints

* All interface text must be in Brazilian Portuguese.
* Do not invent real organizational contact details.
* Use clearly fictional sample data in the administrative dashboard.
* Do not include payment processing or recurring donation functionality.
* Do not add advanced inventory management features such as automated stock alerts, expiry tracking, batch tracking, or forecasting.
* Do not assume that the system replaces every existing process used by the organization.
* Treat the administrative movement model as an initial prototype that can be refined after evaluation with the organization’s coordinator.

## Expected Deliverable

Generate a cohesive, responsive, interactive prototype that includes:

1. Public homepage.
2. Quem Somos section.
3. Nossas Ações section.
4. Como Ajudar section.
5. Contact section.
6. Administrative login.
7. Dashboard overview.
8. Donation movements list.
9. Movement registration form.
10. Movement details and audit history.

The final result should feel like a credible, accessible institutional website paired with a practical, straightforward donation movement management tool for a small nonprofit organization.

Prioritize clarity, usability, and a realistic academic project scope over feature quantity.
