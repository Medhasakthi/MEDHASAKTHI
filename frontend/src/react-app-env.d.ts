/// <reference types="react-scripts" />

// Workaround for lodash type definition issue
declare module 'lodash' {
  const lodash: any;
  export = lodash;
}

declare module 'lodash/*' {
  const lodashModule: any;
  export = lodashModule;
}
