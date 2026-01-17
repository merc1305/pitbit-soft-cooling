---
description: This workflow formalizes the project's requirements and architectural decisions by creating a structured `spec/` directory and synchronizing it with the codebase.
---

### Steps:

1. **Analyze Codebase**: Read the main project files to understand the current implementation and goals.
2. **Setup Spec Directory**: Create a `spec/` directory in the project root.
3. **Generate SDD.md**:
   - Create `spec/SDD.md`.
   - Include: Goal, Scope (MVP), User Scenarios, Functional Requirements, and Definition of Done.
4. **Generate DECISIONS.md**:
   - Create `spec/DECISIONS.md`.
   - Document key architectural choices, rationale, and trade-offs discovered in the code.
5. **Create Spec README**:
   - Create `spec/README.md` with links and descriptions for the specification files.
6. **Update Root README**:
   - Modify or create the root `README.md`.
   - Add a "Development Approach" section explaining that the project follows SDD.
   - Add clear links to the `spec/` directory documents.
7. **Verification & Refinement**:
   - Cross-check the newly created specifications against the actual code.
   - If discrepancies are found, provide a localized refactoring plan to align code with the spec.
8. **Summary**: Provide a walkthrough of the generated documentation.
