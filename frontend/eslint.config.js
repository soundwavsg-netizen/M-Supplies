import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
import reactJSXA11y from 'eslint-plugin-jsx-a11y';
import reactImport from 'eslint-plugin-import';

export default [
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
      
      // JSX formatting - enforce double quotes
      'jsx-quotes': ['error', 'prefer-double'],
      'quotes': ['error', 'single'],
      
      // Import rules
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      
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