import { Badge } from './Badge';

export default {
  title: 'Legacy/Badge',
  component: Badge,
};

const Template = (args) => <Badge {...args} />;

export const Default = Template.bind({});
Default.args = {
  label: 'Queued',
};

export const Solid = Template.bind({});
Solid.args = {
  label: 'Live',
  variant: 'solid',
};

