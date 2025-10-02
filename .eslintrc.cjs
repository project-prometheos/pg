module.exports = {
  root: true,
  extends: ['nx', 'plugin:@nx/react/recommended'],
  parserOptions: {
    project: ['./tsconfig.base.json']
  }
};
