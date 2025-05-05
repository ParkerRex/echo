Step1:
- ask a million questions about codebase
- ask how to make it better 
- ask more questions on why to take that direction
- compare model outputs
- Take another **pass** at it, including relative paths, of existing functionality. include as many referneces to code as possible so it's not liek we're starting from scratch. print the existing file tree before and he after version of the file tree. Expected outputs: 
  - be-prd.txt: Full requirements document
  - [file-structure-comparison.md](http://file-structure-comparison.md): Current vs. proposed structure
  - [implementation-tasks.md](http://implementation-tasks.md): Prioritized implementation tasks
  - examples/: Sample implementations of key components
- Now take everything we spoke about and ensure our @implementation-tasks.md are broken into atomic steps for a junior dev. Include the specific data from the original checklist such that nothing is conceptual, and this list can be given to a developer to implement for production. Do not write any code. If necessary though you can use pseudocode.

Step2: 
- Ask `what would be a good prompt be for telling an anthropic coding assistant on how to get started with this refactor`
- Open new chat 
- paste that in
- review answers
- `Nice - update our @implementation-tasks.md list. Then continue on the next highest leverage ones until its a good stoppping point`
- do this 2x 

**step 3 (new window)**

I need help continuing the refactoring of our video processing pipeline from a monolithic architecture to a clean/hexagonal architecture. We're following a detailed implementation plan and have completed several initial tasks.

Please review these key documents:
- backend/docs/implementation-tasks.md - Contains the step-by-step refactoring plan with completed tasks marked with ✅
- backend/docs/examples/ - Contains code examples for reference
- backend/docs/overview.md - Provides architectural overview and design principles
- backend/docs/file-structure-comparison.md - Shows the before/after structure
- backend/docs/be-prd.txt - Original requirements document