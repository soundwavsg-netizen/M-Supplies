const js = require('@eslint/js');
const globals = require('globals');
const react = require('eslint-plugin-react');
const reactJSXA11y = require('eslint-plugin-jsx-a11y');
const reactImport = require('eslint-plugin-import');

module.exports = [
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
        ...globals.es2020,
        process: 'readonly',
      },
    },
    plugins: {
      react,
      'jsx-a11y': reactJSXA11y,
      import: reactImport,
    },
    rules: {
      // Error on unused variables
      'no-unused-vars': 'error',
      
      // React specific rules
      'react/jsx-uses-react': 'error',
      'react/jsx-uses-vars': 'error',
      'react/prop-types': 'off', // We'll use TypeScript for prop validation later
      
      // JSX formatting - enforce double quotes but warn for now
      'jsx-quotes': ['warn', 'prefer-double'],
      'quotes': ['warn', 'single'],
      
      // Import rules - relaxed for now due to alias issues
      'import/no-unresolved': 'off',
      'import/named': 'warn',
      'import/default': 'warn',
      
      // Accessibility rules
      'jsx-a11y/alt-text': 'warn',
      'jsx-a11y/anchor-has-content': 'warn',
      
      // General code quality
      'no-console': 'warn',
      'no-debugger': 'error',
      'no-duplicate-case': 'error',
      'no-empty': 'error',
      'no-extra-semi': 'error',
      'no-fallthrough': 'error',
      'no-invalid-regexp': 'error',
      'no-irregular-whitespace': 'error',
      'no-unreachable': 'error',
      'use-isnan': 'error',
      'valid-typeof': 'error',
    },
    settings: {
      react: {
        version: 'detect',
      },
      'import/resolver': {
        node: {
          extensions: ['.js', '.jsx', '.ts', '.tsx'],
        },
      },
    },
  },
];