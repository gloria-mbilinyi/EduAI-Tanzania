import {it,expect} from 'vitest';
import {render,screen} from '@testing-library/react';
import {I18nProvider} from '../i18n';
import {AttemptHistory} from '../pages/AssignmentWorkflows';

it('retains all attempts and distinguishes the official score from earlier marks',()=>{
  render(<I18nProvider><AttemptHistory official={3} attempts={[45,80,100].map((score,i)=>({id:i+1,number:i+1,content:`Solution ${i+1}`,grade:{score,feedback:`Feedback ${i+1}`}}))}/></I18nProvider>);
  expect(screen.getAllByRole('progressbar')).toHaveLength(3);
  expect(screen.getByText('Official score')).toBeInTheDocument();
  expect(screen.getByText('Solution 1')).toBeInTheDocument();
  expect(screen.getByText('100% · Feedback 3')).toBeInTheDocument();
});
