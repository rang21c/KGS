import { gql } from "@apollo/client";

export const SEARCH = gql`
  query Search($limit: Int!, $words: String!) {
    search(limit: $limit, words: $words) {
      nodes {
        id
        type
      }
      links {
        source
        target
        label
      }
    }
  }
`;

export const GET_METALIST = gql`
  query Query($value: String!) {
    getMetaList(value: $value) {
      main
      sub
      title
      url
      uploadTime
    }
  }
`;
