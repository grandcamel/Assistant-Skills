/**
 * Scenario rendering routes.
 */

const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const DOMPurify = require('isomorphic-dompurify');
const config = require('../config');

// Load HTML template at module load (cached)
let scenarioTemplate;
try {
  scenarioTemplate = fs.readFileSync(path.join(__dirname, '..', 'templates', 'scenario.html'), 'utf8');
} catch (err) {
  console.error('Failed to load scenario template:', err.message);
  scenarioTemplate = '<!DOCTYPE html><html><body>{{CONTENT}}</body></html>';
}

// HTML escape helper to prevent XSS
const escapeHtml = (str) => str
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#039;');

/**
 * Register scenario routes.
 * @param {Express} app - Express application
 */
function register(app) {
  app.get('/api/scenarios/:name', (req, res) => {
    const scenarioName = req.params.name;
    const scenario = config.SCENARIO_NAMES[scenarioName];

    if (!scenario) {
      return res.status(404).json({ error: 'Scenario not found' });
    }

    const filePath = path.join(config.SCENARIOS_PATH, scenario.file);

    // Path traversal protection: ensure resolved path is within SCENARIOS_PATH
    const resolvedPath = path.resolve(filePath);
    const resolvedBase = path.resolve(config.SCENARIOS_PATH);
    if (!resolvedPath.startsWith(resolvedBase + path.sep) && resolvedPath !== resolvedBase) {
      console.error(`Path traversal attempt blocked: ${filePath} resolved to ${resolvedPath}`);
      return res.status(400).json({ error: 'Invalid path' });
    }

    fs.readFile(resolvedPath, 'utf8', (err, markdown) => {
      if (err) {
        console.error(`Error reading scenario ${scenarioName}:`, err);
        return res.status(404).json({ error: 'Scenario file not found' });
      }

      // Convert markdown to HTML and sanitize to prevent XSS
      const rawHtml = marked(markdown);
      const htmlContent = DOMPurify.sanitize(rawHtml, {
        ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
                       'ul', 'ol', 'li', 'a', 'strong', 'em', 'code', 'pre',
                       'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                       'img', 'span', 'div'],
        ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'id', 'target', 'rel'],
        ALLOW_DATA_ATTR: false
      });

      // Render template with substitutions (escape icon/title to prevent XSS)
      const html = scenarioTemplate
        .replace(/\{\{ICON\}\}/g, escapeHtml(scenario.icon))
        .replace(/\{\{TITLE\}\}/g, escapeHtml(scenario.title))
        .replace(/\{\{CONTENT\}\}/g, htmlContent);

      res.setHeader('Content-Type', 'text/html');
      res.send(html);
    });
  });
}

module.exports = { register };
